# Releasing

First check the status to see available release.

```
make check-releases
```

The next version on master is determined by the version files. E.g:
- `3.3.1-dev0` means the next is a patch, `3.3.1`
- `3.4.0-dev0` means the next is a minor, `3.4.0`


## Regular flow

### Rolling release (master)

Rolling releases are cut from master and they can be minor or patches.
To release whatever is there:

1. Go to the [Rolling Release workflow](https://github.com/dynaconf/dynaconf/actions/workflows/release-rolling.yml)
2. Enter the expected next version (as shown in check-releases)
3. Click the button

If you want the next to be a minor, bump, create a PR and merge it before releasing.

```bash
make bump-minor  # Create bump commit to next minor
```

### Backport release (X.Y branch)

Backport releases are cut from backport branches in the form `X.Y`.
They are always patches.
Assuming there are some unreleased backports commits:

1. Go to the [Backport Release workflow](https://github.com/dynaconf/dynaconf/actions/workflows/release-backport.yml)
2. Enter the expected next version (as shown in check-releases)
3. Click the button

### Publish

The publish workflow is triggered via tag pushes matching `x.y.z`, which happens at each automated release.
To avoid accidental local pushes, these tag pushes are protected via rulesets.

If the release succeeded but the publish fails (or if a manual release is required by some reason),
the publish workflow may be triggered manually.
To do so, run `Actions → Publish → Run workflow` with the tag.

## Learn more

- A minor release will create a `X.(Y-1)` maintenance branch for you.
- Only the last version will trigger a docs publish
- A lot of checks are performed to assure we don't cut a unintended release. E.g:
    - It's not skipping a version
    - We are releasing from the right branch
    - There are unreleased commits to be released (except the post-release commit)
- There is an auxiliary `ci-update` workflow that will create backport PR to update `.github/*` files.
  This is important because dispatches from tags may run outdated publish workflows if they are not kept in sync.
- The publication uses [Trusted Publishing](https://docs.pypi.org/trusted-publishers/), which must be configured in PyPI.
- The release requires content write permissions (push tags). A [Github App](https://docs.github.com/en/apps/overview)
  (DynaconfBot) was created to enable emitting short-lived tokens with well-scoped permission.

### Glossary

Special meaning in the context of this automated workflow:

- **release**: pushing a tagged release commit and a post-release commit upstream
- **release-commit**: a commit with a non-dev version in `dynaconf/VERSION`
- **post-release-commit**: a commit with the next dev version in `dynaconf/VERSION`
- **publish**: publishing the distribution from a tagged release to PyPI, Github Releases and Netlify

