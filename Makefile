SHELL := /bin/bash

# Override with e.g. `make install PYTHON=3.11` to pick the interpreter version.
PYTHON_FLAG := $(if $(PYTHON),--python $(PYTHON))

# Use for running things that requires the project installed
#
# Note: in CI, the install target exports the venv as the default venv, so the
# the workflow can use it without calling uv.
RUN := $(if $(CI),,uv run --no-sync $(PYTHON_FLAG))

# Use for running things independent of project state. Usage: $(call RUN_TOOL,<group>)
RUN_TOOL = uv run --isolated $(PYTHON_FLAG) $(if $(1),--only-group $(1))

# Lowest Python version we support (pyproject.toml's requires-python) - minification
# must run on it for the resulting bytecode to stay compatible with all supported versions.
PYTHON_LOWERBOUND := 3.10

# Windows and macOS are excluded: their integration tests' docker fixtures
# aren't reliable there (macOS GitHub-hosted runners have no Docker at all).
CITEST_FULL := $(if $(CI),$(if $(filter Windows macOS,$(RUNNER_OS)),,1))

# Pytest flags
PYTEST_COV := --cov-config pyproject.toml --cov=dynaconf
SHORT_TB := --tb=short

# Override with e.g. `make test k=test_something` to run a single test by name/expression.
K_FILTER = $(if $(k),-k "$(k)")
# This outcome is a report on what test failed, succeeded, etc
OUTCOME_REPORT = --junitxml=junit/$(1)-results.xml

ifeq ($(RUNNER_OS),Windows)
VENV_BIN := .venv/Scripts
else
VENV_BIN := .venv/bin
endif

.PHONY: help
help:
	@python scripts/makefile_doc.py < $(MAKEFILE_LIST)


# ---------------------------------------------------------------------------
# General
# ---------------------------------------------------------------------------

.PHONY: all tips lint docs docs-build

#: Clean, install dev deps, lint, and run the full test suite
all: clean install lint test test-functional
	$(RUN) coverage report

#: Lint and format the code
lint:
	$(call RUN_TOOL,lint) pre-commit run --all-files

#: Serve the documentation site locally with live-reload
docs: _check-venv
	$(RUN) mkdocs serve

#: Build the documentation site
docs-build: _check-venv
	rm -rf site
	$(RUN) mkdocs build --clean

#: Remove build artifacts, caches, and generated files
clean:
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name '__pycache__' -prune -exec rm -rf {} \;
	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;
	rm -rf .cache
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	rm -rf htmlcov
	rm -rf .tox/
	rm -rf site
	rm -rf tmp-bench
	rm -rf .venv

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

.PHONY: install clean info _check-venv

_check-venv:
	@if [ ! -d .venv ]; then \
		echo "ERROR: No .venv found. Run 'make install' first."; \
		exit 1; \
	fi

#: Create .venv and install project | [WHEEL=<path>] [GROUP=<group>] [PYTHON=<version>] [ARGS=<uv-args>]
install:
	uv venv --clear $(PYTHON_FLAG)
	uv pip install \
		$(if $(WHEEL),$(WHEEL),--editable .) \
		--group $(if $(GROUP),$(GROUP),dev) \
		$(ARGS)
	@[ -n "$$GITHUB_PATH" ] && echo "$(CURDIR)/$(VENV_BIN)" >> "$$GITHUB_PATH" || true
	@[ -n "$$GITHUB_ENV" ] && echo "VIRTUAL_ENV=$(CURDIR)/$(VENV_DIR)" >> $$GITHUB_ENV || true

#: Show info of local venv (.venv) | [VERBOSE=1] full pip list
info:
	@if [ ! -d .venv ]; then \
		echo "No .venv found. Run 'make install' first."; \
	else \
		echo "Path:   $(CURDIR)/.venv"; \
		echo "Python: $$($(VENV_BIN)/python --version 2>&1)"; \
		echo; \
		$(if $(VERBOSE), \
			uv pip list, \
			uv pip show dynaconf dynaconf-release-utility; \
			echo -e "\n---\nFor full package list:\nmake info VERBOSE=1" \
		); \
	fi

#: Show quick usage tips
tips:
	@echo "- Behavior can differ when the CI env var is set: some targets (test, install, lint) adapt automatically."
	@echo "- Auto re-run tests on change: find . -name '*.py' | entr make test"

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

.PHONY: test test-integration test-functional test-redis test-vault test-all bench

#: Run the unit test suite with coverage | [k=<expr>] run tests matching <expr>
test: _check-venv
	$(RUN) pytest tests/ \
		-m "not integration" \
		-v -l --color=yes $(SHORT_TB) $(K_FILTER) \
		$(if $(k),--disable-warnings,$(PYTEST_COV)) \
		$(if $(CITEST_FULL),$(call OUTCOME_REPORT,test))
	$(if $(k),,$(if $(CITEST_FULL),$(RUN) coverage xml))

#: Run integration-marked tests only | [k=<expr>] run tests matching <expr>
test-integration: _check-venv
	$(RUN) pytest tests/ \
		-m "integration" \
		-v -l --color=yes $(SHORT_TB) $(K_FILTER) \
		$(if $(k),--disable-warnings,$(PYTEST_COV) --cov-append) \
		$(if $(CITEST_FULL),$(call OUTCOME_REPORT,integration))
	$(if $(k),,$(if $(CITEST_FULL),$(RUN) coverage xml))

#: Run the functional test suite | [k=<expr>] run tests matching <expr>
test-functional: _check-venv
	$(RUN) python tests_functional/runtests.py $(if $(k),--filter "$(k)")

#: Run functional tests against a local Redis
test-redis: _check-venv
	$(RUN) ./tests_functional/test_redis.sh

#: Run functional tests against a local Vault
test-vault: _check-venv
	$(RUN) ./tests_functional/test_vault.sh
	$(RUN) ./tests_functional/test_vault_userpass.sh

#: Run every test suite and generate an HTML coverage report
test-all: test-functional test-integration test-redis test-vault test
	$(RUN) coverage html

#: Run performance benchmarks
bench:
	rm -rf tmp-bench
	@scripts/bench.sh depth2_getitem
	@scripts/bench.sh depth2_getattr
	@scripts/bench.sh depth1_getattr
	@scripts/bench.sh depth1_setattr

# ---------------------------------------------------------------------------
# Build & Release
# ---------------------------------------------------------------------------

.PHONY: build check-releases release-notes bump-minor

#: Build the sdist and wheel
build: clean
	# create a new dynaconf/vendor folder with minified files
	$(call RUN_TOOL,release) --python $(PYTHON_LOWERBOUND) ./scripts/minify.sh
	@uv build
	# restore dynaconf/vendor_src folder as dynaconf/vendor
	@./scripts/source_vendor.sh
	.github/scripts/dist-health-check.sh
	ls -la dist

#: Check for pending releases | Release via https://github.com/dynaconf/dynaconf/actions)
check-releases:
	$(call RUN_TOOL,release) release-utility check

#: Preview release notes
release-notes:
	$(call RUN_TOOL,release) git-changelog --release-notes

#: Bump X.Y.Z.dev to X.(Y+1).0.dev | [YES=1] create the bump commit (DEFAULT=dry-run)
bump-minor:
	$(if $(YES), \
		@$(call RUN_TOOL,release) bump-my-version bump minor --commit && \
		echo -e "Bump commit created!\n" && \
		git log -1 --stat, \
		@NEXT=$$($(call RUN_TOOL,release) bump-my-version show --increment minor new_version); \
		echo "Next version would be: $$NEXT"; \
		echo -e "To create the bump commit, run:\n"; \
		echo "make bump-minor YES=1" \
	)
