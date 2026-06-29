#!/usr/bin/env python3
"""
Release utility for dynaconf.

Exit codes:
    0 — success
    1 — one or more checks failed or a step errored
"""

import argparse
import datetime
import functools
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from abc import ABC
from abc import abstractmethod
from typing import NamedTuple
from typing import Optional

from git_changelog import build_and_render
from git_changelog import read_config
from packaging.version import InvalidVersion
from packaging.version import Version

BUMP_FILES = [
    "CHANGELOG.md",
    "dynaconf/VERSION",
    "mkdocs.yml",
    "pyproject.toml",
]
RELEASE_COMMIT_MSG = "Release version {version}"
CI_UPDATE_MSG = "chore(ci): CI update from master ({sha})"
GITHUB_REPO = "dynaconf/dynaconf"
GITHUB_API = "https://api.github.com"
REPO_URL = f"https://github.com/{GITHUB_REPO}.git"
PYPI_URL = "https://pypi.org/pypi/dynaconf/json"
RUNNING_CI = bool(os.getenv("CI"))


@functools.cache
def _fetch_github_login(sha: str) -> Optional[str]:
    """Return the GitHub login for a commit SHA, or None on any failure."""
    url = f"{GITHUB_API}/repos/{GITHUB_REPO}/commits/{sha}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    token = os.getenv("GITHUB_API_TOKEN") or os.getenv("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    debug(
        "github_login_fetch",
        f"{'authenticated' if token else 'unauthenticated'} [{sha[:7]}]",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        author = data.get("author")
        return author["login"] if author else None
    except Exception as e:
        debug("github_login_fetch_error", f"{sha[:7]}: {e}")
        return None


def github_author_link(commit) -> str:
    """Return a markdown GitHub profile link, falling back to the git author name."""
    login = _fetch_github_login(commit.hash)
    if login:
        return f"@{login}"
    return commit.author_name


def _write_github_output(key: str, value: str) -> None:
    path = os.getenv("GITHUB_OUTPUT")
    if path:
        with open(path, "a") as f:
            f.write(f"{key}={value}\n")


def fetch_pypi_versions() -> list[str]:
    """Return the list of versions published on PyPI for dynaconf."""
    try:
        with urllib.request.urlopen(PYPI_URL, timeout=10) as response:
            data = json.loads(response.read())
    except urllib.error.HTTPError as e:
        raise InvalidReleaseError(
            f"Failed to fetch PyPI versions from {PYPI_URL!r}: {e}"
        ) from e
    result = list(data["releases"].keys())
    debug("pypi_versions", sorted(result, key=Version))
    return result


DEFAULT_BRANCH = "master"


class InvalidReleaseError(Exception):
    pass


# Keep line breaks on the help display
HELP_FORMATTER = argparse.RawDescriptionHelpFormatter


_DEBUG = True


def debug(label: str, value: object) -> None:
    if _DEBUG:
        print(f"[DEBUG] {label}: {value}", file=sys.stderr)  # noqa: T201


def info(msg: str) -> None:
    print(msg)  # noqa: T201


class Repository:
    """Git repository introspection."""

    def _git(self, *args) -> tuple[str, str]:
        result = subprocess.run(
            ["git", *args], check=True, capture_output=True, text=True
        )
        return result.stdout.strip(), result.stderr.strip()

    def _git_ok(self, *args) -> bool:
        result = subprocess.run(["git", *args], capture_output=True)
        return result.returncode == 0

    # --- read-only ---

    def current_branch(self) -> str:
        # --abbrev-ref resolves HEAD to the short branch name (e.g. "master").
        # In detached HEAD state it returns the literal string "HEAD".
        result, _ = self._git("rev-parse", "--abbrev-ref", "HEAD")
        debug("current_branch", result)
        return result

    def root(self) -> str:
        # --show-toplevel always returns an absolute path regardless of which
        # subdirectory the process was launched from.
        result, _ = self._git("rev-parse", "--show-toplevel")
        debug("root", result)
        return result

    def working_tree_status(self) -> str:
        # --porcelain is a stable machine-readable format that is unaffected by
        # locale or git version. Empty output means the tree is clean.
        result, _ = self._git("status", "--porcelain")
        debug("working_tree_status", repr(result) if result else "clean")
        return result

    def sync_counts(
        self, url: str, branch: str = DEFAULT_BRANCH
    ) -> tuple[int, int]:
        """Return (ahead, behind) commit counts relative to the remote branch."""
        # Fetch by URL, not by remote name, so this works regardless of how
        # the user has their remotes configured.
        self.fetch(url, branch)
        # FETCH_HEAD is always written by the fetch above, so these counts
        # reflect exactly what was just fetched — no stale remote-tracking ref.
        ahead_out, _ = self._git("rev-list", "--count", "FETCH_HEAD..HEAD")
        behind_out, _ = self._git("rev-list", "--count", "HEAD..FETCH_HEAD")
        ahead, behind = int(ahead_out), int(behind_out)
        debug("sync_counts", f"ahead={ahead}, behind={behind}")
        return ahead, behind

    def local_version_tags(self) -> list[str]:
        # git tag emits one exact tag name per line with no decorations,
        # so splitting on newlines gives a precise list for membership checks.
        # Non-version tags (e.g. "list", "latest") are silently skipped.
        output, _ = self._git("tag", "--list")
        tags = []
        for tag in output.splitlines():
            try:
                Version(tag)
                tags.append(tag)
            except InvalidVersion:
                pass
        debug("local_version_tags", sorted(tags, key=Version))
        return tags

    def remote_version_tags(self, url: str) -> list[str]:
        # Queries the remote directly over the git protocol without touching
        # any local clone state, so the result always reflects the server.
        # Non-version tags are silently skipped.
        output, _ = self._git("ls-remote", "--tags", url)
        tags = []
        no_version_tags = []
        for line in output.splitlines():
            ref = line.split("\t")[1]
            if ref.endswith("^{}"):
                continue
            tag = ref.removeprefix("refs/tags/")
            try:
                Version(tag)
                tags.append(tag)
            except InvalidVersion:
                no_version_tags.append(tag)
                pass
        debug("remote_not_version_tags", sorted(no_version_tags))
        debug("remote_version_tags", sorted(tags, key=Version))
        return tags

    def commits_between(self, from_ref: str, to_ref: str) -> list[str]:
        # --format=%H emits one bare hash per line with no decorations,
        # making it locale-independent and stable across git versions.
        output, _ = self._git("log", f"{from_ref}..{to_ref}", "--format=%H")
        result = output.splitlines()
        debug("commits_between", result)
        return result

    def shortlog_since(self, tag: str, indent: int = 0) -> str:
        output, _ = self._git("shortlog", f"{tag}..")
        if not indent:
            return output
        prefix = " " * indent
        return "\n".join(
            f"{prefix}{line}" if line else "" for line in output.splitlines()
        )

    def user_identity(self) -> tuple[str, str]:
        name, _ = self._git("config", "user.name")
        email, _ = self._git("config", "user.email")
        return name, email

    def branch_exists(self, name: str) -> bool:
        return self._git_ok("rev-parse", "--verify", f"refs/heads/{name}")

    def branch_tip(self, name: str) -> str:
        tip, _ = self._git("rev-parse", f"refs/heads/{name}")
        return tip

    def is_ancestor(self, commit: str, of: str) -> bool:
        return self._git_ok("merge-base", "--is-ancestor", commit, of)

    def remote_branches(self, url: str, pattern: str = "") -> list[str]:
        args = ["ls-remote", "--heads", url]
        if pattern:
            args.append(pattern)
        output, _ = self._git(*args)
        result = []
        for line in output.splitlines():
            ref = line.split("\t")[1]
            result.append(ref.removeprefix("refs/heads/"))
        return result

    def show_file(self, ref: str, path: str) -> str:
        result, _ = self._git("show", f"{ref}:{path}")
        return result

    def fetch(self, url: str, branch: str = "", *, tags: bool = False) -> None:
        args = ["fetch", url]
        if branch:
            args.append(branch)
        if tags:
            args.extend(["--tags", "--force"])
        self._git(*args)

    def rev_parse(self, ref: str, *, short: bool = False) -> str:
        args = ["rev-parse"]
        if short:
            args.append("--short")
        args.append(ref)
        result, _ = self._git(*args)
        return result

    def staged_files(self) -> list[str]:
        output, _ = self._git("diff", "--cached", "--name-only")
        return output.splitlines()

    def checkout_path_from_ref(self, ref: str, path: str) -> None:
        self._git("checkout", ref, "--", path)

    def fetch_branch_tip(self, url: str, branch: str) -> str:
        """Fetch a remote branch and return its tip commit hash."""
        self.fetch(url, branch)
        tip, _ = self._git("rev-parse", "FETCH_HEAD")
        return tip

    # --- write ---

    def stage(self, files: list[str]) -> None:
        self._git("add", *files)

    def commit(self, *messages: str) -> None:
        args = ["commit"]
        for msg in messages:
            args += ["--message", msg]
        self._git(*args)

    def create_tag(self, name: str, message: str) -> None:
        self._git("tag", "--annotate", name, "--message", message)

    def create_branch(self, name: str, at: str = "HEAD") -> None:
        self._git("branch", name, at)


class VersionBumper:
    """Wraps bump-my-version calls."""

    def _bmv(self, *args) -> tuple[str, str]:
        result = subprocess.run(
            ["bump-my-version", *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip(), result.stderr.strip()

    def calculated_next(self) -> str:
        result, _ = self._bmv("show", "--increment", "pre", "new_version")
        debug("calculated_next_version", result)
        return result

    def bump_to_release(self) -> str:
        """Bump dev -> release and return the new version string."""
        self._bmv("bump", "pre")
        version, _ = self._bmv("show", "current_version")
        return version

    def bump_to_next_dev(self) -> None:
        self._bmv("bump", "patch", "--commit")

    def update_changelog(self, version: str) -> None:
        settings = read_config()
        settings["bump"] = version
        settings.setdefault("jinja_context", {})["github_author_link"] = (
            github_author_link
        )
        build_and_render(**settings)


class Releaser(ABC):
    def __init__(self, repo: Repository, bumper: VersionBumper) -> None:
        self.repo = repo
        self.bumper = bumper

    @abstractmethod
    def validate(
        self, expected: str, *, pre_publish: bool = False
    ) -> None: ...

    @abstractmethod
    def release(self, *, yes: bool = False) -> None: ...

    def _cut_release(self, previous: str) -> str:
        info("[BUMP] Bumping version files: x.y.z-dev0 -> x.y.z")
        current_version = self.bumper.bump_to_release()

        info(f"[BUMP] Updating changelog for {current_version}")
        self.bumper.update_changelog(current_version)
        self.repo.stage(BUMP_FILES)
        shortlog = self.repo.shortlog_since(previous, indent=4)
        today = datetime.date.today().isoformat()
        name, email = self.repo.user_identity()

        info(f"[COMMIT] Creating release commit for {current_version}")
        self.repo.commit(
            RELEASE_COMMIT_MSG.format(version=current_version),
            "Shortlog of commits since last release:",
            shortlog,
        )
        self.repo.create_tag(
            current_version, f"Released in {today} by {name} <{email}>"
        )

        info(
            "[COMMIT] Creating post-release bump commit: x.y.z -> x.y.next-dev0"
        )
        self.bumper.bump_to_next_dev()

        return current_version

    def _confirm(self, yes: bool) -> None:
        if not yes:
            answer = input("Type 'yes' to confirm: ")
            if answer.strip().lower() != "yes":
                print("[ABORTED] Release cancelled.", file=sys.stderr)  # noqa: T201
                sys.exit(2)

    @staticmethod
    def get_release_type(tag: str, remote_tags: list[str]) -> str:
        """Return 'rolling' if tag is in the latest (major, minor) series, 'backport' otherwise."""
        latest = max(remote_tags, key=Version)
        tag_xy = Version(tag).release[:2]
        latest_xy = Version(latest).release[:2]
        return "backport" if tag_xy < latest_xy else "rolling"


class RollingReleaser(Releaser):
    def validate(self, expected: str, *, pre_publish: bool = False) -> None:
        pypi_versions = fetch_pypi_versions()
        remote_tags = self.repo.remote_version_tags(REPO_URL)

        debug("mode", "pre_publish" if pre_publish else "release")
        debug("running_ci", RUNNING_CI)
        debug("expected", expected)
        debug("repo_url", REPO_URL)
        debug("pypi_url", PYPI_URL)
        debug("latest_remote_tag", max(remote_tags, key=Version))

        if pre_publish:
            check_version_format(expected)
            check_tag_exists_on_remote(self.repo, expected)
            prior_tags = [t for t in remote_tags if t != expected]
            check_is_contiguous(expected, prior_tags)
            check_is_unique(expected, pypi_versions)
            check_is_contiguous(expected, pypi_versions)
        else:
            calculated = self.bumper.calculated_next()
            debug("next_version", calculated)
            check_on_release_branch(self.repo)
            check_version_matches_expected(calculated, expected)
            check_clean_working_tree(self.repo)
            if not RUNNING_CI:
                check_no_local_tag(self.repo, expected)
                check_in_sync_with_upstream(self.repo)
            check_has_unreleased_commits(self.repo, remote_tags)
            check_version_format(expected)
            check_is_unique(expected, pypi_versions)
            check_is_contiguous(expected, pypi_versions)
            check_is_unique(expected, remote_tags)
            check_is_contiguous(expected, remote_tags)

        info(f"[OK] Release {expected!r} passed all validation checks.")

    def _create_backport_branch(self, major: int, minor: int) -> Optional[str]:
        prev_branch = f"{major}.{minor - 1}"
        prev_tags = [
            t
            for t in self.repo.local_version_tags()
            if Version(t).release[:2] == (major, minor - 1)
        ]
        if self.repo.branch_exists(prev_branch):
            info(f"[BRANCH] {prev_branch} already exists, skipping")
        elif prev_tags:
            last_prev_tag = max(prev_tags, key=Version)
            anchor = self.repo.commits_between(last_prev_tag, "HEAD")[-1]
            self.repo.create_branch(prev_branch, at=anchor)
            info(
                f"[BRANCH] Created backport branch: {prev_branch} at {anchor[:7]}"
            )
            return prev_branch
        else:
            info(f"[BRANCH] No {prev_branch} tags found, skipping")
        return None

    def release(self, *, yes: bool = False) -> None:
        previous = max(self.repo.local_version_tags(), key=Version)
        next_version = self.bumper.calculated_next()
        info(f"Previous release : {previous}")
        info(f"Next release     : {next_version}")
        self.validate(next_version)
        self._confirm(yes)
        current_version = self._cut_release(previous)

        major, minor, patch = Version(current_version).release
        # Last tag from 3.2 is broken (not in a branch). Revert after 3.3.0 release
        # if patch == 0 and minor > 0:
        #     # New minor release: create the X.(Y-1) maintenance branch anchored at
        #     # the post-release bump of the last X.(Y-1) tag, not at the current HEAD.
        #     branch = self._create_backport_branch(major, minor)
        #     if branch:
        #         _write_github_output("backport-branch", branch)

        info("[COMMIT] Done.")


class BackportReleaser(Releaser):
    @staticmethod
    def _filter_series(
        versions: list[str],
        *,
        by_xy: Optional[tuple[int, int]] = None,
        exclude: Optional[list[str]] = None,
    ) -> list[str]:
        if by_xy is not None and exclude is not None:
            raise ValueError("by_xy and exclude are mutually exclusive")
        if by_xy is not None:
            major, minor = by_xy
            return [
                v for v in versions if Version(v).release[:2] == (major, minor)
            ]
        if exclude is not None:
            return [v for v in versions if v not in exclude]
        return list(versions)

    def validate(self, expected: str, *, pre_publish: bool = False) -> None:
        pypi_versions = fetch_pypi_versions()
        remote_tags = self.repo.remote_version_tags(REPO_URL)
        major, minor, _ = Version(expected).release

        debug("mode", "backport-publish" if pre_publish else "backport")
        debug("running_ci", RUNNING_CI)
        debug("expected", expected)
        debug("repo_url", REPO_URL)
        debug("pypi_url", PYPI_URL)

        series_remote = self._filter_series(remote_tags, by_xy=(major, minor))
        series_pypi = self._filter_series(pypi_versions, by_xy=(major, minor))

        if pre_publish:
            prior_series = self._filter_series(
                series_remote, exclude=[expected]
            )
            check_version_format(expected)
            check_tag_exists_on_remote(self.repo, expected)
            check_tag_on_backport_branch(self.repo, expected)
            check_tag_has_real_commits(self.repo, expected, series_remote)
            check_is_contiguous(expected, prior_series)
            check_is_unique(expected, pypi_versions)
            check_is_contiguous(expected, series_pypi)
        else:
            local_tags = self.repo.local_version_tags()
            series_local = self._filter_series(
                local_tags, by_xy=(major, minor)
            )
            calculated = self.bumper.calculated_next()
            debug("next_version", calculated)
            check_on_backport_branch(self.repo, expected)
            check_is_patch_release(expected)
            check_version_format(expected)
            check_version_matches_expected(calculated, expected)
            check_clean_working_tree(self.repo)
            if not RUNNING_CI:
                check_no_local_tag(self.repo, expected)
                check_in_sync_with_upstream(
                    self.repo, branch=f"{major}.{minor}"
                )
            check_has_unreleased_commits(self.repo, series_local)
            check_is_unique(expected, pypi_versions)
            check_is_unique(expected, remote_tags)
            check_is_contiguous(expected, series_remote)

        info(f"[OK] Release {expected!r} passed all validation checks.")

    def release(self, *, yes: bool = False) -> None:
        next_version = self.bumper.calculated_next()
        info(f"Next release     : {next_version}")
        self.validate(next_version)

        major, minor, _ = Version(next_version).release
        series_local = self._filter_series(
            self.repo.local_version_tags(), by_xy=(major, minor)
        )
        previous = max(series_local, key=Version)
        info(f"Previous release : {previous}")
        self._confirm(yes)
        self._cut_release(previous)
        info("[COMMIT] Done.")


def check_version_format(version: str) -> None:
    """Raise if `version` is not a clean X.Y.Z release (no pre-release suffix)."""
    v = Version(version)
    if v.is_prerelease or v.is_postrelease or v.local:
        raise InvalidReleaseError(
            f"{version!r} is not a clean release version (expected X.Y.Z)"
        )


def check_version_matches_expected(calculated: str, expected: str) -> None:
    """Raise if the calculated version does not match the expected version.

    Guards against releasing the wrong version when the branch has already
    been bumped beyond what was intended.
    """
    if calculated != expected:
        raise InvalidReleaseError(
            f"Calculated version {calculated!r} does not match expected {expected!r}"
        )


def check_is_unique(version: str, released: list[str]) -> None:
    """Raise if `version` is already present in `released`."""
    if not released:
        raise InvalidReleaseError("Released list cannot be empty")
    if version in released:
        raise InvalidReleaseError(f"{version!r} is already released")


def check_is_contiguous(version: str, released: list[str]) -> None:
    """Raise if `version` is not a contiguous increment from the latest in `released`.

    For example, if the latest release is 3.2.4, only 3.2.5, 3.3.0, or 4.0.0
    are valid. A jump to 3.2.6 or 3.4.0 would be rejected.
    """
    if not released:
        raise InvalidReleaseError("Released list cannot be empty")
    latest = max(released, key=Version)
    lat_x, lat_y, lat_z = Version(latest).release
    new_x, new_y, new_z = Version(version).release
    valid = (
        (new_x, new_y, new_z) == (lat_x, lat_y, lat_z + 1)
        or (new_x, new_y, new_z) == (lat_x, lat_y + 1, 0)
        or (new_x, new_y, new_z) == (lat_x + 1, 0, 0)
    )
    if not valid:
        raise InvalidReleaseError(
            f"{version!r} is not a contiguous increment from {latest!r}"
        )


def check_on_release_branch(
    repo: Repository, *, is_backport_release: bool = False
) -> None:
    """Raise if the current branch is not the expected release branch."""
    if is_backport_release:
        raise NotImplementedError
    branch = repo.current_branch()
    if branch != DEFAULT_BRANCH:
        raise InvalidReleaseError(
            f"Branch {branch!r} is not an allowed release branch"
        )


def check_on_backport_branch(repo: Repository, version: str) -> None:
    """Raise if the current branch is not the X.Y maintenance branch for `version`."""
    branch = repo.current_branch()
    major, minor, _ = Version(version).release
    expected = f"{major}.{minor}"
    if branch != expected:
        raise InvalidReleaseError(
            f"Branch {branch!r} does not match version {expected!r} required for a {version!r} backport release."
        )


def check_is_patch_release(version: str) -> None:
    """Raise if `version` is not a patch (Z > 0) release.

    Backport branches only ever produce patch releases. Minor and major bumps
    belong on master.
    """
    _, _, patch = Version(version).release
    if patch == 0:
        raise InvalidReleaseError(
            f"{version!r} is not a patch release (Z=0). "
            "Backport branches can only produce patch releases — "
            "bump the minor version on master instead."
        )


def check_no_local_tag(repo: Repository, version: str) -> None:
    """Raise if `version` already exists as a local git tag."""
    if version in repo.local_version_tags():
        raise InvalidReleaseError(
            f"Tag {version!r} already exists locally. "
            f"Consider removing it with: git tag -d {version} "
            f"(only if it does not exist upstream)."
        )


def check_tag_exists_on_remote(repo: Repository, version: str) -> None:
    """Raise if `version` does not exist as a remote git tag."""
    if version not in repo.remote_version_tags(REPO_URL):
        raise InvalidReleaseError(
            f"Tag {version!r} does not exist on remote {REPO_URL!r}"
        )


def check_tag_has_real_commits(
    repo: Repository, version: str, series: list[str]
) -> None:
    """Raise if the tag contains only the release commit and no real changes.

    Checks commits between the previous tag in the series and `version`.
    The release commit itself is always present, so at least 2 commits are required.
    """
    prior = [t for t in series if t != version]
    if not prior:
        return
    previous = max(prior, key=Version)
    commits = repo.commits_between(previous, version)
    if len(commits) <= 1:
        raise InvalidReleaseError(
            f"Tag {version!r} contains no real commits since {previous!r} "
            f"(only the release commit found)"
        )


def check_tag_on_backport_branch(repo: Repository, version: str) -> None:
    """Raise if the tag commit is not reachable from the expected maintenance branch."""
    major, minor, _ = Version(version).release
    branch = f"{major}.{minor}"
    repo.fetch(REPO_URL, branch)
    if not repo.is_ancestor(version, "FETCH_HEAD"):
        raise InvalidReleaseError(
            f"Tag {version!r} is not on the {branch!r} maintenance branch — "
            f"backport releases must be tagged from the maintenance branch."
        )


def check_in_sync_with_upstream(
    repo: Repository, branch: str = DEFAULT_BRANCH
) -> None:
    """Raise if the local branch is ahead, behind, or diverged from the remote branch."""
    ahead, behind = repo.sync_counts(REPO_URL, branch)
    if ahead > 0 and behind > 0:
        raise InvalidReleaseError(
            f"Branch has diverged: {ahead} commit(s) ahead, {behind} behind upstream"
        )
    if behind > 0:
        raise InvalidReleaseError(
            f"Branch is {behind} commit(s) behind upstream"
        )
    if ahead > 0:
        raise InvalidReleaseError(
            f"Branch is {ahead} commit(s) ahead of upstream"
        )


def check_has_unreleased_commits(repo: Repository, series: list[str]) -> None:
    """Raise if there are no real commits since the latest tag in `series`.

    The first commit after a release tag is always the post-release bump
    (e.g. 3.2.4 → 3.2.5.dev0), so at least two commits are required.
    """
    if not series:
        raise InvalidReleaseError(
            "No local tags found for this series — "
            "ensure the repository was cloned with full history (fetch-depth: 0)"
        )
    latest_tag = max(series, key=Version)
    commits = repo.commits_between(latest_tag, "HEAD")
    if len(commits) <= 1:
        raise InvalidReleaseError(
            f"No unreleased commits since {latest_tag!r} "
            f"(only the post-release bump commit found)"
        )


def check_clean_working_tree(repo: Repository) -> None:
    """Raise if the working tree has any staged, unstaged, or untracked changes."""
    status = repo.working_tree_status()
    if status:
        raise InvalidReleaseError(f"Working tree is not clean:\n{status}")


def update_github_files(repo: Repository) -> bool:
    """Overwrite .github/ with master's version and commit if changed. Returns True if committed."""
    repo.fetch(REPO_URL, DEFAULT_BRANCH)
    sha = repo.rev_parse("FETCH_HEAD", short=True)
    repo.checkout_path_from_ref("FETCH_HEAD", ".github/")
    if not repo.staged_files():
        info("[OK] .github/ already up to date.")
        return False
    repo.commit(CI_UPDATE_MSG.format(sha=sha))
    info(f"[OK] .github/ committed from master ({sha}).")
    return True


class BranchStatus(NamedTuple):
    branch: str
    current: Optional[str]
    next_version: Optional[str]
    unreleased: int


def get_backport_branches(repo: Repository) -> list[str]:
    """Return the last two X.Y maintenance branches from the remote, newest first."""
    all_remote = repo.remote_branches(REPO_URL, "[0-9]*.[0-9]*")
    xy = [
        b
        for b in all_remote
        if len(b.split(".")) == 2 and all(p.isdigit() for p in b.split("."))
    ]
    return sorted(xy, key=lambda b: Version(b + ".0"), reverse=True)[:2]


def _collect_branch_statuses(
    repo: Repository, branches: list[str], local_tags: list[str]
) -> list[BranchStatus]:
    statuses = []
    for branch in branches:
        if branch == DEFAULT_BRANCH:
            local_series = local_tags
        else:
            major, minor = (int(x) for x in branch.split("."))
            local_series = [
                t
                for t in local_tags
                if Version(t).release[:2] == (major, minor)
            ]

        if not local_series:
            statuses.append(BranchStatus(branch, None, None, 0))
            continue

        current = max(local_series, key=Version)
        tip = repo.fetch_branch_tip(REPO_URL, branch)
        raw = repo.show_file("FETCH_HEAD", "dynaconf/VERSION")
        next_v = Version(raw).base_version
        commits = repo.commits_between(current, tip)
        count = max(
            0, len(commits) - 1
        )  # exclude the post-release bump commit
        statuses.append(BranchStatus(branch, current, next_v, count))
    return statuses


def _print_branch_table(statuses: list[BranchStatus]) -> None:
    rows = [
        (
            s.branch,
            s.current or "—",
            s.next_version or "—",
            f"{s.unreleased} commits" if s.unreleased > 0 else "—",
        )
        for s in statuses
    ]
    headers = ("Branch", "Current", "Next", "Unreleased")
    widths = [
        max(len(headers[i]), max(len(r[i]) for r in rows))
        for i in range(len(headers))
    ]
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    info(fmt.format(*headers))
    for row in rows:
        info(fmt.format(*row))


def check_release_status(repo: Repository) -> None:
    """Print available releases and unpublished tags."""
    repo.fetch(REPO_URL, tags=True)
    local_tags = repo.local_version_tags()
    pypi_versions = fetch_pypi_versions()
    branches = [DEFAULT_BRANCH] + get_backport_branches(repo)

    statuses = _collect_branch_statuses(repo, branches, local_tags)
    _print_branch_table(statuses)

    info("Unpublished releases")
    active_series = {
        tuple(int(x) for x in b.split("."))
        for b in branches
        if b != DEFAULT_BRANCH
    }
    unpublished = sorted(
        [
            t
            for t in local_tags
            if t not in pypi_versions
            and Version(t).release[:2] in active_series
        ],
        key=Version,
        reverse=True,
    )
    if unpublished:
        for tag in unpublished:
            info(f"  {tag}")
    else:
        info("  —")


def run_from_root(repo: Repository) -> None:
    os.chdir(repo.root())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=HELP_FORMATTER
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate a release before or after tagging",
        formatter_class=HELP_FORMATTER,
    )
    validate_parser.add_argument(
        "version", help="Expected release version (e.g. 3.3.0)"
    )
    validate_parser.add_argument(
        "--pre-publish",
        action="store_true",
        help="Run publish-mode checks (tag already on remote, not yet on PyPI)",
    )
    validate_parser.add_argument(
        "--backport",
        action="store_true",
        help="Run backport-mode checks (patch release from an X.Y maintenance branch)",
    )

    rolling_parser = subparsers.add_parser(
        "rolling-release",
        help="Cut a VCS/git tagged release from whatever version is on main (no PyPI publish)",
        description=(
            "Cut a VCS/git tagged release from whatever version is currently on main.\n\n"
            "Does not publish to PyPI. Steps: bump dev -> release, update changelog, "
            "commit, tag, then bump to next dev.\n\n"
            "GitHub Actions output (written to GITHUB_OUTPUT when CI=true):\n"
            "  backport-branch  Name of the X.(Y-1) maintenance branch created for a new\n"
            "                   minor release (e.g. '3.5' after releasing 3.6.0). Not set\n"
            "                   for patch releases."
        ),
        formatter_class=HELP_FORMATTER,
    )
    rolling_parser.add_argument(
        "-y", "--yes", action="store_true", help="Skip confirmation prompt"
    )

    backport_parser = subparsers.add_parser(
        "backport-release",
        help="Cut a patch release from an X.Y maintenance branch (no PyPI publish)",
        description=(
            "Cut a patch release from the current X.Y maintenance branch.\n\n"
            "Does not publish to PyPI. Steps: bump dev -> release, update changelog, "
            "commit, tag, then bump to next dev. Must be run on an X.Y branch."
        ),
        formatter_class=HELP_FORMATTER,
    )
    backport_parser.add_argument(
        "-y", "--yes", action="store_true", help="Skip confirmation prompt"
    )

    get_parser = subparsers.add_parser(
        "get",
        help="Print a computed release value and exit",
        description=(
            "Print a computed release value and exit.\n\n"
            "Supported items:\n"
            "  backport-branch  The X.Y maintenance branch for a given tag (e.g. 3.5.2 → '3.5'). Requires VALUE.\n"
            "  is-latest        'true' if VALUE is greater than all versions on PyPI, 'false' otherwise. Requires VALUE.\n"
            "  next-version     The calculated next release version (e.g. 3.3.2-dev0 → '3.3.2')\n"
            "  release-type     Whether a tag is a 'rolling' or 'backport' release (requires VALUE=<tag>)"
        ),
        formatter_class=HELP_FORMATTER,
    )
    get_parser.add_argument(
        "item",
        choices=[
            "backport-branch",
            "backport-branches",
            "is-latest",
            "next-version",
            "release-type",
        ],
        help="The value to retrieve",
    )
    get_parser.add_argument(
        "value",
        nargs="?",
        help="Tag name (required for release-type)",
    )

    subparsers.add_parser(
        "update-github",
        help="Overwrite .github/ with the version from master",
        formatter_class=HELP_FORMATTER,
    )

    subparsers.add_parser(
        "check",
        help="Show available releases and unpublished tags",
        formatter_class=HELP_FORMATTER,
    )

    return parser


def run(args: argparse.Namespace) -> None:
    repo = Repository()
    bumper = VersionBumper()
    if not (args.command == "check"):
        run_from_root(repo)

    if args.command == "validate":
        cls = BackportReleaser if args.backport else RollingReleaser
        cls(repo, bumper).validate(args.version, pre_publish=args.pre_publish)
    elif args.command == "rolling-release":
        RollingReleaser(repo, bumper).release(yes=args.yes)
    elif args.command == "backport-release":
        BackportReleaser(repo, bumper).release(yes=args.yes)
    elif args.command == "update-github":
        if not update_github_files(repo):
            sys.exit(1)
    elif args.command == "check":
        global _DEBUG
        _DEBUG = False
        check_release_status(repo)
    elif args.command == "get":
        if args.item == "backport-branch":
            if not args.value:
                sys.exit(1)
            major, minor, _ = Version(args.value).release
            info(f"{major}.{minor}")
        elif args.item == "is-latest":
            if not args.value:
                sys.exit(1)
            pypi_versions = fetch_pypi_versions()
            is_latest = not pypi_versions or Version(args.value) > Version(
                max(pypi_versions, key=Version)
            )
            info("true" if is_latest else "false")
        elif args.item == "next-version":
            info(bumper.calculated_next())
        elif args.item == "backport-branches":
            for b in get_backport_branches(repo):
                info(b)
        elif args.item == "release-type":
            remote_tags = repo.remote_version_tags(REPO_URL)
            info(Releaser.get_release_type(args.value, remote_tags))


def main() -> None:
    _args = build_parser().parse_args()
    try:
        run(_args)
    except InvalidReleaseError as e:
        print(f"[ERROR] {e}", file=sys.stderr)  # noqa: T201
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {e}", file=sys.stderr)  # noqa: T201
        if e.stderr:
            print(e.stderr, file=sys.stderr)  # noqa: T201
        sys.exit(2)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)  # noqa: T201
        sys.exit(2)


if __name__ == "__main__":
    main()
