"""Tests for release_utility.py (fetchers excluded — they perform I/O)."""

from unittest.mock import MagicMock

import pytest
from release_utility import check_clean_working_tree
from release_utility import check_has_unreleased_commits
from release_utility import check_in_sync_with_upstream
from release_utility import check_is_contiguous
from release_utility import check_is_unique
from release_utility import check_no_local_tag
from release_utility import check_on_release_branch
from release_utility import check_tag_exists_on_remote
from release_utility import check_tag_on_backport_branch
from release_utility import check_version_format
from release_utility import check_version_matches_expected
from release_utility import fetch_pypi_versions
from release_utility import InvalidReleaseError
from release_utility import Releaser
from release_utility import REPO_URL
from release_utility import Repository


class TestFetchers:
    # 3.2.0 up to 3.2.13 are released
    KNOWN_VERSIONS = {f"3.2.{p}" for p in range(14)}

    @pytest.mark.integration
    def test_fetch_pypi_versions_returns_list_containing_known_versions(self):
        versions = fetch_pypi_versions()
        assert isinstance(versions, list)
        assert self.KNOWN_VERSIONS.issubset(versions)

    @pytest.mark.integration
    def test_fetch_remote_tags_returns_list_containing_known_tags(self):
        tags = Repository().remote_version_tags(REPO_URL)
        assert isinstance(tags, list)
        assert self.KNOWN_VERSIONS.issubset(tags), (
            f"Known tags not in repo: {REPO_URL}"
        )


class TestCheckVersionMatchesExpected:
    @pytest.mark.parametrize(
        "calculated,expected",
        [
            pytest.param("3.3.0", "3.3.0", id="exact-match"),
            pytest.param("3.2.4", "3.2.4", id="exact-match-other"),
        ],
    )
    def test_passes(self, calculated, expected):
        check_version_matches_expected(calculated, expected)

    @pytest.mark.parametrize(
        "calculated,expected",
        [
            pytest.param("3.3.1", "3.3.0", id="calculated-ahead-of-expected"),
            pytest.param("3.2.4", "3.3.0", id="calculated-behind-expected"),
        ],
    )
    def test_raises(self, calculated, expected):
        with pytest.raises(
            InvalidReleaseError, match=rf"{calculated}.*{expected}"
        ):
            check_version_matches_expected(calculated, expected)


class TestCheckNotExists:
    @pytest.mark.parametrize(
        "version,released",
        [
            pytest.param("3.3.0", ["3.2.3", "3.2.4"], id="not-in-list"),
        ],
    )
    def test_passes(self, version, released):
        check_is_unique(version, released)

    @pytest.mark.parametrize(
        "version,released",
        [
            pytest.param("3.2.4", ["3.2.3", "3.2.4"], id="matches-latest"),
            pytest.param("3.2.3", ["3.2.3", "3.2.4"], id="matches-older"),
            pytest.param("3.3.0", [], id="empty-list"),
        ],
    )
    def test_raises(self, version, released):
        with pytest.raises(InvalidReleaseError):
            check_is_unique(version, released)


class TestCheckIsContiguous:
    @pytest.mark.parametrize(
        "version,released",
        [
            pytest.param("3.2.5", ["3.2.3", "3.2.4"], id="patch-bump"),
            pytest.param("3.3.0", ["3.2.3", "3.2.4"], id="minor-bump"),
            pytest.param("4.0.0", ["3.2.3", "3.2.4"], id="major-bump"),
        ],
    )
    def test_passes(self, version, released):
        check_is_contiguous(version, released)

    @pytest.mark.parametrize(
        "version,released",
        [
            pytest.param("3.2.6", ["3.2.3", "3.2.4"], id="patch-jump"),
            pytest.param("3.4.0", ["3.2.3", "3.2.4"], id="minor-jump"),
            pytest.param("5.0.0", ["3.2.3", "3.2.4"], id="major-jump"),
            pytest.param(
                "3.3.1", ["3.2.3", "3.2.4"], id="minor-bump-not-from-zero"
            ),
            pytest.param(
                "4.0.1", ["3.2.3", "3.2.4"], id="major-bump-not-from-zero"
            ),
            pytest.param("3.2.3", ["3.2.3", "3.2.4"], id="older-version"),
            pytest.param("3.3.0", [], id="empty-list"),
        ],
    )
    def test_raises(self, version, released):
        with pytest.raises(InvalidReleaseError):
            check_is_contiguous(version, released)


class TestCheckOnReleaseBranch:
    @pytest.mark.parametrize(
        "branch",
        [
            pytest.param("master", id="master"),
        ],
    )
    def test_passes(self, branch):
        repo = MagicMock()
        repo.current_branch.return_value = branch
        check_on_release_branch(repo)

    @pytest.mark.parametrize(
        "branch",
        [
            pytest.param("feature/foo", id="feature-branch"),
            pytest.param("HEAD", id="detached-head"),
        ],
    )
    def test_raises(self, branch):
        repo = MagicMock()
        repo.current_branch.return_value = branch
        with pytest.raises(InvalidReleaseError):
            check_on_release_branch(repo)

    def test_raises_for_non_master(self):
        repo = MagicMock()
        repo.current_branch.return_value = "3.3"
        with pytest.raises(InvalidReleaseError):
            check_on_release_branch(repo)


class TestCheckCleanWorkingTree:
    def test_passes(self):
        repo = MagicMock()
        repo.working_tree_status.return_value = ""
        check_clean_working_tree(repo)

    @pytest.mark.parametrize(
        "status",
        [
            pytest.param("M  file.py", id="staged-changes"),
            pytest.param(" M file.py", id="unstaged-changes"),
            pytest.param("?? file.py", id="untracked-files"),
        ],
    )
    def test_raises(self, status):
        repo = MagicMock()
        repo.working_tree_status.return_value = status
        with pytest.raises(InvalidReleaseError):
            check_clean_working_tree(repo)


class TestCheckInSyncWithUpstream:
    def test_passes(self):
        repo = MagicMock()
        repo.sync_counts.return_value = (0, 0)
        check_in_sync_with_upstream(repo)

    @pytest.mark.parametrize(
        "ahead,behind",
        [
            pytest.param(0, 3, id="behind"),
            pytest.param(2, 0, id="ahead"),
            pytest.param(1, 1, id="diverged"),
        ],
    )
    def test_raises(self, ahead, behind):
        repo = MagicMock()
        repo.sync_counts.return_value = (ahead, behind)
        with pytest.raises(InvalidReleaseError):
            check_in_sync_with_upstream(repo)


class TestCheckNoLocalTag:
    def test_passes(self):
        repo = MagicMock()
        repo.local_version_tags.return_value = ["3.2.14"]
        check_no_local_tag(repo, "3.3.0")

    def test_raises(self):
        repo = MagicMock()
        repo.local_version_tags.return_value = ["3.2.14", "3.3.0"]
        with pytest.raises(InvalidReleaseError):
            check_no_local_tag(repo, "3.3.0")


class TestCheckTagOnBackportBranch:
    def test_passes_when_tag_is_on_maintenance_branch(self):
        repo = MagicMock()
        repo.is_ancestor.return_value = True
        check_tag_on_backport_branch(repo, "3.4.3")
        repo.fetch.assert_called_once_with(REPO_URL, "3.4")
        repo.is_ancestor.assert_called_once_with("3.4.3", "FETCH_HEAD")

    def test_raises_when_tag_is_not_on_maintenance_branch(self):
        repo = MagicMock()
        repo.is_ancestor.return_value = False
        with pytest.raises(
            InvalidReleaseError, match="not on the '3.4' maintenance branch"
        ):
            check_tag_on_backport_branch(repo, "3.4.3")


class TestCheckTagExistsOnRemote:
    def test_passes(self):
        repo = MagicMock()
        repo.remote_version_tags.return_value = ["3.2.14", "3.3.0"]
        check_tag_exists_on_remote(repo, "3.3.0")

    def test_raises(self):
        repo = MagicMock()
        repo.remote_version_tags.return_value = ["3.2.14"]
        with pytest.raises(
            InvalidReleaseError, match="does not exist on remote"
        ):
            check_tag_exists_on_remote(repo, "3.3.0")


class TestCheckHasUnreleasedCommits:
    @pytest.mark.parametrize(
        "commits",
        [
            pytest.param(
                ["abc123", "def456", "ghi789"], id="multiple-changes"
            ),
            pytest.param(["abc123", "def456"], id="one-change-plus-bump"),
        ],
    )
    def test_passes(self, commits):
        repo = MagicMock()
        repo.commits_between.return_value = commits
        check_has_unreleased_commits(repo, ["3.2.4"])

    @pytest.mark.parametrize(
        "commits",
        [
            pytest.param(["abc123"], id="only-post-release-bump"),
            pytest.param([], id="tag-at-head"),
        ],
    )
    def test_raises(self, commits):
        repo = MagicMock()
        repo.commits_between.return_value = commits
        with pytest.raises(InvalidReleaseError, match="No unreleased commits"):
            check_has_unreleased_commits(repo, ["3.2.4"])

    def test_raises_for_empty_series(self):
        repo = MagicMock()
        with pytest.raises(InvalidReleaseError, match="No local tags found"):
            check_has_unreleased_commits(repo, [])


class TestCheckIsAllowedRelease:
    @pytest.mark.parametrize(
        "version",
        [
            pytest.param("3.3.0", id="clean"),
            pytest.param("1.0.0", id="clean-major"),
            pytest.param("3.2.4", id="clean-patch"),
        ],
    )
    def test_passes(self, version):
        check_version_format(version)

    @pytest.mark.parametrize(
        "version",
        [
            pytest.param("3.3.0-dev0", id="dev-suffix"),
            pytest.param("3.3.0.dev0", id="dev-suffix-dot"),
            pytest.param("3.3.0a1", id="alpha-suffix"),
            pytest.param("3.3.0b1", id="beta-suffix"),
            pytest.param("3.3.0rc1", id="rc-suffix"),
        ],
    )
    def test_raises(self, version):
        with pytest.raises(InvalidReleaseError):
            check_version_format(version)


class TestGetReleaseType:
    TAGS = ["3.3.0", "3.3.1", "3.3.4", "3.4.0", "3.5.0", "3.5.1"]

    @pytest.mark.parametrize(
        "tag,expected",
        [
            pytest.param(
                "3.5.1", "rolling", id="latest-patch-in-latest-series"
            ),
            pytest.param("3.5.0", "rolling", id="first-in-latest-series"),
            pytest.param("3.3.4", "backport", id="patch-in-older-series"),
            pytest.param("3.3.0", "backport", id="first-in-older-series"),
            pytest.param("3.4.0", "backport", id="older-minor-series"),
            pytest.param(
                "3.5.2", "rolling", id="next-rolling-not-yet-in-remote"
            ),
            pytest.param(
                "3.4.1", "backport", id="next-backport-not-yet-in-remote"
            ),
        ],
    )
    def test_release_type(self, tag, expected):
        assert Releaser.get_release_type(tag, self.TAGS) == expected
