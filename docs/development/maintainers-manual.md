# Maintainers Manual

## Release/Publish Process

**TLDR:** Publish/release is going to use current committed version and bump the next patch.
If we want the next release to be a minor/major, we should [create a bump](#prepare-for-a-y-release-minor) before publishing.

### Overview

The [new release process](#releasepublish-process) considers the committed version (e.g, present in `dynaconf/VERSION` and other files) the current version of that commit.
In practical terms, it usually corresponds to the version (but in development stage) that we want to release next.

For example, if we have something like `x.y.z.dev0`, that means we are developmening version `x.y.z`, which is the version we pretend to release next.
After we do the release, the version will be automatically bumped to the next patch development version `x.y.next.dev0`, where `next=z+1`.

If we need to do a Y-release instead of a Z-release, we should [bump the version](#prepare-for-a-y-release-minor) and merge it before triggering a new release.
This can happen either in a PR that we know should be a *minor* or in some PR later on.

### Guides

Before proceeding, make sure you have an active venv with `requirements.txt` installed.
For publishing, you'll also require configuring you PyPI credentials.

#### Create and publish a release

To create a release, push it to master and publish the package, run:

```bash
make release
git push --tags git@github.com:dynaconf/dynaconf master
make publish
```

#### Prepare for a Y release (minor)

To update the version in files which contain version to the next **minor** version, run the command below.
This can be used in a dedicated bump-PR or alongside a feature you're working.

```bash
make bump-minor
```

### Reference

#### Publish/Release process

The publish/release process is based on [this issue](https://github.com/dynaconf/dynaconf/issues/1072)
and can be summarized:

1. `make release`:
    1. **Create a release-commit + build**
        * Updates the changelog.
        * Bump `x.y.z.dev0` to `x.y.z`.
        * Builds the package on `dist/`
    1. **Create a bump-commit**
        * Bump to next Z development version `z.y.next.dev0`
1. `git push ...`:
    * Push both commits to master with the new tag
1. `make publish`:
    1. **Publish to PyPI** using `dist/`
    1. **Publish to Github** using tagged commit and new changelog entries

#### Related Tools

- [bump-my-version]()
- [git-changelog]()
- [twine]()
