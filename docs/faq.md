# Frequently Asked Questions

Here are some curated questions about Dynaconf usage.

- To get more help, please use the [GitHub discussions](https://github.com/dynaconf/dynaconf/issues).
- If you'd like to suggest some new questions here, use [GitHub issues](https://github.com/dynaconf/dynaconf/discussions).

---

## Dynamically set `settings_files` path

> I have multiple environments and I don't want to rely on a particular location of the settings file. How do I set its path dynamically?

[Dynaconf-specific config options](https://www.dynaconf.com/configuration/), such as `settings_file` or `settings_files`, have two ways of being defined:

- On instance options: `Dynaconf(settings_file="path.to.settings.toml")`
- On environment options: `export SETTINGS_FILE_FOR_DYNACONF="path.to.settings"`

So, for each environment, just export the right path for it. Note that it should be UPPERCASE and have `_FOR_DYNACONF ` suffix

Environment settings will, by default, override instance settings.

## Problem running tests in IDE

> I'm trying to run a test on my IDE, but there it raises an `OSError: Starting path not found` exception, although running from CLI works fine. What can it be?

Dynaconf path resolving relies on your CWD (current working directory) being at the project's root.
Some IDEs may modify the CWD to run tests, and this will cause this issue.

PyCharm, for example, may change the CWD to `./tests` in their integrated test system. If this is your specific case, go to "Modify Run Configuration > Working Dir" on the test tab and assure that it points to the root of your project.

## Conditional Validation

> Is it possible to create a Validator that would require the presence of an option if another option is present?

Yes. Validators provide great flexibility in the ways you can arrange them. If `foo` must only be present if `bar` exists, you could do:

```python
Validator(
        "foo",
        must_exist=True,
        when=Validator(
            "bar", must_exist=True,
        ),
    ),
```

See more about [validators](https://www.dynaconf.com/validation/)

## Deprecation mechanism

> I have a quite busy project and sometimes old config files get in the way. Is there a deprecation mechanism to deal with this?

There is already a [feature request](https://github.com/dynaconf/dynaconf/discussions/881) about a more specific deprecation mechanism, but right now you can use hooks to achieve that. You might do something like:

```python
# dynaconf_hooks.py
def post(settings: Dynaconf) -> dict:
    DEPRECATED = {
        "FOO": "NEWKEY"
    }
    for key, new in DEPRECATED.items():
        if value := settings.get(key):
            warnings.warn(f"{key} has been replaced by {new}")
            settings.set(new, value)
```

See more about [hooks](https://www.dynaconf.com/advanced/#hooks)
