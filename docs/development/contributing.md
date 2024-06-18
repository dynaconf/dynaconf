# Contributing

When contributing to this repository, please first discuss the change you wish to make via issue,
email, or any other method with the owners of this repository before making a change.

Please note we have a [code of conduct](code-of-conduct.md), please follow it in all your interactions with the project.

[This Diagram](https://viewer.diagrams.net/?highlight=0000ff&edit=_blank&layers=1&nav=1&title=Dynaconf#Uhttps%3A%2F%2Fdrive.google.com%2Fuc%3Fid%3D11krXcDr67FGci_f36FZO-hiL08z4FuL9%26export%3Ddownload)
an help you understand visually what happens on Dynaconf.

Additional links:

- [dynaconf-dev Matrix](https://app.element.io/#/room/#dynaconf_dev:gitter.im)
- [Maintainer Meetings notes](https://hackmd.io/NJggYilJQ1uvA0wsHIoHmw?view)

## Pull Request Process

1. Ensure your local environment is set.
    1. Clone your own fork of this repo
    2. Activate a python3.9+ virtualenv
    3. Write the code
2. Update the `docs/guides/` related to your changes.
3. Update `tests_functional/` (editing or adding a new one related to your changes)
4. Ensure tests are passing (see below `make all`)
    1. This project uses `pre-commit` and `Ruff` for code styling and adequacy tests.
5. Commit, Push and make a Pull Request!


### Common Workflow


#### Prepare your environment

```bash
# clone your fork of this repo
git clone git@github.com:{$USER}/dynaconf.git

# Add the upstream remote
git remote add upstream https://github.com/dynaconf/dynaconf.git

# Activate your Python Environment
python3.9 -m venv venv
source venv/bin/activate

# Install dynaconf for development
make all

```

#### Work on a task

```bash
# Checkout to a working branch
git checkout -b my_feature

# Open your favorite editor (VSCode for example)
code .

# After editing please rebase with upstream. Fix any conflicts if any.
git fetch upstream; git rebase upstream/master

# Update docs/guides/ if needed

# Edit tests_functional/ if needed

# Create a new app in tests_functional/{your_example}

# Run your test in isolation for quick iterations
tests_functional/runtests.py --filter {your_example}

# Then ensure everything is ok
make all
```

#### Submit your PR

```bash
# Now commit your changes
git commit -am "Changed XPTO to fix #issue_number"

# Push to your own fork
git push -u origin HEAD

# Open github.com/dynaconf/dynaconf and send a Pull Request.
```

### Run integration tests

* `make all` do not run integration tests for Redis and Vault.
* If you want to run integration tests, make sure you have `docker` and `docker-compose`
installed.

```bash

# To install docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
<output truncated>

# To permit your user run docker commands without sudo
sudo usermod -aG docker {$USER}

# Run complete integration tests
make test_integration

# or Run functional example tests individually
make test_redis
make test_vault
```

