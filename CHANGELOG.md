Changelog
=========


2.0.1 (2019-04-22)
------------------
- Release version 2.0.1. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (17):
            Release version 2.0.0
            Added Django explicit mode to docs (#149)
            HOTIX: Django doc
            Logger is now cached (removed logging import time overhead)
            Update issue templates
            Adjusts issue templates
            Fix Typo in issue template
            fix #160 - invoking directory should not be search breaking point.
            Add explicit call to main() on cli.py (#165)
            Generate coverage.xml file (#167)
            Fix #166 renamed GLOBAL_ENV_ to ENVVAR_PREFIX_ (#168)
            Fix #169 renamed SETTINGS_MODULE_ to SETTINGS_FILE_ (#170)
            HOTFIX config.md on docs [skip ci] (#171)
            Fix some open file descriptors on exampls and tests (#172)
            Fix #151 setup pre-commit and black (#173)
            Add CONTRIBUTING.md, conrtib isntructions and Black badge (#174)
            Fix release script

      David Moreau Simard (1):
            Fix typos in bash export examples

      Jan Willhaus (2):
            Skip reloading envs for validators that only apply to current_env (#162)
            Fix #163 Allow disabling env prefix (#164)
- Fix release script. [Bruno Rocha]
- Add CONTRIBUTING.md, conrtib isntructions and Black badge (#174)
  [Bruno Rocha]
- Fix #151 setup pre-commit and black (#173) [Bruno Rocha]

  * Add pre-commit to makefile

  * Fix #151 setup pre-commit and black
- Fix some open file descriptors on exampls and tests (#172) [Bruno
  Rocha]
- HOTFIX config.md on docs [skip ci] (#171) [Bruno Rocha]
- Fix #169 renamed SETTINGS_MODULE_ to SETTINGS_FILE_ (#170) [Bruno
  Rocha]

  Backwards compatibility maintained!
- Fix #166 renamed GLOBAL_ENV_ to ENVVAR_PREFIX_ (#168) [Bruno Rocha]

  * Fix #166 renamed GLOBAL_ENV_ to ENVVAR_PREFIX_

  See #166

  * Added django compat example
- Generate coverage.xml file (#167) [Bruno Rocha]
- Add explicit call to main() on cli.py (#165) [Bruno Rocha]

  To use click-web tool the module should be able to be explicitly called. `python -m dynaconf.cli`
- Fix #163 Allow disabling env prefix (#164) [Jan Willhaus, janw
  <mail@janwillhaus.de>    * Update docs for use of False instead of
  none]

  * Allow setting GLOBAL_ENV to "" or NoneType to remove prefix

  * Allow for underscore-only prefix with empty string GLOBAL_ENV

  * Test cases for the different GLOBAL_ENV settings

  * Update docs, add usage example

  * Apply suggestions from code review
- Skip reloading envs for validators that only apply to current_env
  (#162) [Jan Willhaus]

  * Simplify control flow for single-env use-cases

  * Ensure uppercase env/current_env

  * Add test not reloading env with validation in same env

  * Pep8 compliance

  * Change mock call assertions for support in Py3.5
- Fix #160 - invoking directory should not be search breaking point.
  [Bruno Rocha]

  Search should stop at breaking point  only if ROOT_PATH is defined
- Fix Typo in issue template. [Bruno Rocha]
- Adjusts issue templates. [Bruno Rocha]
- Update issue templates. [Bruno Rocha]
- Logger is now cached (removed logging import time overhead) [Bruno
  Rocha]

  Debugged using:

  `python3.7 -X importtime -c 'import app'` and `python3.7 -X importtime -c 'import dynaconf'`

  Found that the tries to import `logzero` were consuming 0.1us (not so much, but we dont want it)

  removed logzero, cached logger using lru_cache (that means that if loglevel changes, log changes)

  - imporved docs and badges.
- Fix typos in bash export examples. [David Moreau Simard]
- HOTIX: Django doc. [Bruno Rocha]
- Added Django explicit mode to docs (#149) [Bruno Rocha]
- Release version 2.0.0. [Bruno Rocha]

  Shortlog of commits since last release:

      Aaron DeVore (1):
            GH-111: Fix MERGE_ENABLED merging settings with themselves

      Bruno Rocha (21):
            Merge branch 'jperras-merge-multiple-settings-files'
            Merge branch 'master' of github.com:rochacbruno/dynaconf
            Fix #106 make PROJECT_ROOT_FOR_DYNACONF to work with custom paths
            Update dynaconf/utils/boxing.py
            Update dynaconf/utils/boxing.py
            Add release script and CHANGELOG in place of history.
            Release version 1.2.0
            Tox is now part of pre-publish command
            Drop Python 3.4
            Release version 1.2.1
            add top contributors
            Fix #129 on settings file, single keys should be case insensitive.
            Fix #125 settings_module not being set on .configure()
            Fix #127 add configurable yaml loader method, default to full_load
            Fix #122 allow disable of core loaders, added examples.
            Fix #117 add support for extra secrets file (like for jenkins CI)
            Fix #110 add docs for dynaconf_include
            Add dynaconf_include examples
            Set up CI with Azure Pipelines (#142)
            Add dynaconf_merge fucntionality for dict and list settings. (#139)
            Preparing for 2.0.0

      Byungjin Park (1):
            Fix typo

      Jaepil Koh (1):
            Update django.md

      Joel Perras (3):
            Allow dotted-path based setting of configuration key/value pairs.
            Handle nested includes in settings files.
            Remove extraneous lines.

      Mantas (3):
            Add INSTANCE_FOR_DYNACONF and --instance
            Remove mocker fixture
            Python 3.4 has different error message

      Matthias (1):
            Fix small typo in README.md

      Pete Savage (1):
            Fix exponential slow down when loader is run multiple times

      Raoul Snyman (1):
            Add environments into the path in Vault so that the same Vault server can be used for multiple environments

      mspinelli (2):
            fixed infinite recursion caused by copy()
            add tests for dynabox fix


2.0.0 (2019-04-09)
------------------
- Release version 2.0.0. [Bruno Rocha]

  Shortlog of commits since last release:

      Aaron DeVore (1):
            GH-111: Fix MERGE_ENABLED merging settings with themselves

      Bruno Rocha (21):
            Merge branch 'jperras-merge-multiple-settings-files'
            Merge branch 'master' of github.com:rochacbruno/dynaconf
            Fix #106 make PROJECT_ROOT_FOR_DYNACONF to work with custom paths
            Update dynaconf/utils/boxing.py
            Update dynaconf/utils/boxing.py
            Add release script and CHANGELOG in place of history.
            Release version 1.2.0
            Tox is now part of pre-publish command
            Drop Python 3.4
            Release version 1.2.1
            add top contributors
            Fix #129 on settings file, single keys should be case insensitive.
            Fix #125 settings_module not being set on .configure()
            Fix #127 add configurable yaml loader method, default to full_load
            Fix #122 allow disable of core loaders, added examples.
            Fix #117 add support for extra secrets file (like for jenkins CI)
            Fix #110 add docs for dynaconf_include
            Add dynaconf_include examples
            Set up CI with Azure Pipelines (#142)
            Add dynaconf_merge fucntionality for dict and list settings. (#139)
            Preparing for 2.0.0

      Byungjin Park (1):
            Fix typo

      Jaepil Koh (1):
            Update django.md

      Joel Perras (3):
            Allow dotted-path based setting of configuration key/value pairs.
            Handle nested includes in settings files.
            Remove extraneous lines.

      Mantas (3):
            Add INSTANCE_FOR_DYNACONF and --instance
            Remove mocker fixture
            Python 3.4 has different error message

      Matthias (1):
            Fix small typo in README.md

      Pete Savage (1):
            Fix exponential slow down when loader is run multiple times

      Raoul Snyman (1):
            Add environments into the path in Vault so that the same Vault server can be used for multiple environments

      mspinelli (2):
            fixed infinite recursion caused by copy()
            add tests for dynabox fix
- Preparing for 2.0.0. [Bruno Rocha]

  Dynaconf 2.0.0

  - Fix #129 get_fresh should be case insensitive
  - Fix #125 .configure was not loading `settings_module` passed as argument
  - Fix #127 fix YAML warnings and default to full_load
  - Allow disable of core loaders #122
  - Added support for Jenkins secrets file #117
  - Added more examples for includes #110
  - Moved to Azure Pipelines CI #142
  - Added 100% test coverage on windows (Unit & Functional tests)
  - Deprecated MERGE_ENABLED in favor of local dynaconf_merge
  - Fix #74 - Better File Searching (now building a reasonable Search Tree)
  - Now it finds settings when invoking from out of Script folder
  - Fixed test environment (each test now run in a separate tmpdir)
  - Added a check to avoid Circular references when starting settings inside settings
  - Added Django Extension v2 with better syntax and a lot od `inspect` instrospetion
  - Updated documentation about new features
  - Added a not that YAML is the recommended format for Django
  - Added support for Django Standalone Script
  - Added support for Django unit testing
  - Fix #148 `env` was not being passed to custom loaders
  - Fix #144 removed `six` as it is a Py3.4+ only project
  - Added Backwards compatibility for users using old django Extension
  - start_dotenv is now Lazy (only when settings._setup is called)
  - Added new _FOR_DYNACONF config options ENV_SWITCHER, SKIP_FILES, INCLUDES & SECRETS
  - Renamed config PROJECT_ROOT -> ROOT_PATH
- Add dynaconf_merge fucntionality for dict and list settings. (#139)
  [Bruno Rocha]

  If your settings has existing variables of types `list` ot `dict` and you want to `merge` instead of `override` then
  the `dynaconf_merge` and `dynaconf_merge_unique` stanzas can mark that variable as a candidate for merging.

  For **dict** value:

  Your main settings file (e.g `settings.toml`) has an existing `DATABASE` dict setting on `[default]` env.

  Now you want to contribute to the same `DATABASE` key by addind new keys, so you can use `dynaconf_merge` at the end of your dict:

  In specific `[envs]`

  ```toml
  [default]
  database = {host="server.com", user="default"}

  [development]
  database = {user="dev_user", dynaconf_merge=true}

  [production]
  database = {user="prod_user", dynaconf_merge=true}
  ```

  In an environment variable:

  ```bash
  export DYNACONF_DATABASE='{password=1234, dynaconf_merge=true}'
  ```

  Or in an additional file (e.g `settings.yaml, .secrets.yaml, etc`):

  ```yaml
  default:
    database:
      password: 1234
      dynaconf_merge: true
  ```

  The `dynaconf_merge` token will mark that object to be merged with existing values (of course `dynaconf_merge` key will not be added to the final settings it is jsut a mark)

  The end result will be on `[development]` env:

  ```python
  settings.DATABASE == {'host': 'server.com', 'user': 'dev_user', 'password': 1234}
  ```

  The same can be applied to **lists**:

  `settings.toml`
  ```toml
  [default]
  plugins = ["core"]

  [development]
  plugins = ["debug_toolbar", "dynaconf_merge"]
  ```

  And in environment variable

  ```bash
  export DYNACONF_PLUGINS='["ci_plugin", "dynaconf_merge"]'
  ```

  Then the end result on `[development]` is:

  ```python
  settings.PLUGINS == ["ci_plugin", "debug_toolbar", "core"]
  ```

  The `dynaconf_merge_unique` is the token for when you want to avoid duplications in a list.

  Example:

  ```toml
  [default]
  scripts = ['install.sh', 'deploy.sh']

  [development]
  scripts = ['dev.sh', 'test.sh', 'deploy.sh', 'dynaconf_merge_unique']
  ```

  ```bash
  export DYNACONF_SCRIPTS='["deploy.sh", "run.sh", "dynaconf_merge_unique"]'
  ```

  The end result for `[development]` will be:

  ```python
  settings.SCRIPTS == ['install.sh', 'dev.sh', 'test.sh', 'deploy.sh', 'run.sh']
  ```

  > Note that `deploy.sh` is set 3 times but it is not repeated in the final settings.

  The **dynaconf_merge** functionality works only for the first level keys, it will not merge subdicts or nested lists (yet).
- Set up CI with Azure Pipelines (#142) [Bruno Rocha]

  - setup azure pipelines ci
  - remove travis
  - fix windows support
- Add dynaconf_include examples. [Bruno Rocha]
- Fix #110 add docs for dynaconf_include. [Bruno Rocha]

  fix #110
- Fix #117 add support for extra secrets file (like for jenkins CI)
  [Bruno Rocha]

  Now it is possible to export SECRETS_FOR_DYNACONF and have this
  extra point loaded, like in a Jenkins CI you can specify on job.

  ```yaml
  secret_file:
    variable: SECRETS_FOR_DYNACONF
    credentials:
      type: specific_credentials
      value: /path/to/secrets_file.toml{json,ini,yaml,py}

  ```

  That variable can also be a list of paths.
- Fix #122 allow disable of core loaders, added examples. [Bruno Rocha]
- Fix #127 add configurable yaml loader method, default to full_load.
  [Bruno Rocha]
- Fix #125 settings_module not being set on .configure() [Bruno Rocha]
- Fix #129 on settings file, single keys should be case insensitive.
  [Bruno Rocha]
- GH-111: Fix MERGE_ENABLED merging settings with themselves. [Aaron
  DeVore]
- Add top contributors. [Bruno Rocha]
- Release version 1.2.1. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (9):
            Merge branch 'jperras-merge-multiple-settings-files'
            Merge branch 'master' of github.com:rochacbruno/dynaconf
            Fix #106 make PROJECT_ROOT_FOR_DYNACONF to work with custom paths
            Update dynaconf/utils/boxing.py
            Update dynaconf/utils/boxing.py
            Add release script and CHANGELOG in place of history.
            Release version 1.2.0
            Tox is now part of pre-publish command
            Drop Python 3.4

      Byungjin Park (1):
            Fix typo

      Jaepil Koh (1):
            Update django.md

      Joel Perras (3):
            Allow dotted-path based setting of configuration key/value pairs.
            Handle nested includes in settings files.
            Remove extraneous lines.

      Mantas (3):
            Add INSTANCE_FOR_DYNACONF and --instance
            Remove mocker fixture
            Python 3.4 has different error message

      Matthias (1):
            Fix small typo in README.md

      Pete Savage (1):
            Fix exponential slow down when loader is run multiple times

      Raoul Snyman (1):
            Add environments into the path in Vault so that the same Vault server can be used for multiple environments

      mspinelli (2):
            fixed infinite recursion caused by copy()
            add tests for dynabox fix


1.2.1 (2019-03-11)
------------------
- Release version 1.2.1. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (9):
            Merge branch 'jperras-merge-multiple-settings-files'
            Merge branch 'master' of github.com:rochacbruno/dynaconf
            Fix #106 make PROJECT_ROOT_FOR_DYNACONF to work with custom paths
            Update dynaconf/utils/boxing.py
            Update dynaconf/utils/boxing.py
            Add release script and CHANGELOG in place of history.
            Release version 1.2.0
            Tox is now part of pre-publish command
            Drop Python 3.4

      Byungjin Park (1):
            Fix typo

      Jaepil Koh (1):
            Update django.md

      Joel Perras (3):
            Allow dotted-path based setting of configuration key/value pairs.
            Handle nested includes in settings files.
            Remove extraneous lines.

      Mantas (3):
            Add INSTANCE_FOR_DYNACONF and --instance
            Remove mocker fixture
            Python 3.4 has different error message

      Matthias (1):
            Fix small typo in README.md

      Pete Savage (1):
            Fix exponential slow down when loader is run multiple times

      Raoul Snyman (1):
            Add environments into the path in Vault so that the same Vault server can be used for multiple environments

      mspinelli (2):
            fixed infinite recursion caused by copy()
            add tests for dynabox fix
- Fix exponential slow down when loader is run multiple times. [Pete
  Savage]

  * When using context managers, the loader is invoked each time.
    This was slowing down in an exponential manner each time the it was run.
    The eventual cause of this was down to an attribute being used as a list.
    The object merge dutifully tried to expand this item out again and again
    even in the case that the list was a single item, resulting in [item],
    becoming [item, item]. The next time the merge was run, this process was
    run again, but for each item in the list. In this particular instance
    the list was identical, it meant that the list grew exponentially.
  * This fix is a short optimization that checks to see if the old list
    is identical to the new list. In which case, there is no merge to complete
    so we simply return.
- Add environments into the path in Vault so that the same Vault server
  can be used for multiple environments. [Raoul Snyman]
- Fix typo. [Byungjin Park]
- Drop Python 3.4. [Bruno Rocha]
- Tox is now part of pre-publish command. [Bruno Rocha]
- Release version 1.2.0. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (6):
            Merge branch 'jperras-merge-multiple-settings-files'
            Merge branch 'master' of github.com:rochacbruno/dynaconf
            Fix #106 make PROJECT_ROOT_FOR_DYNACONF to work with custom paths
            Update dynaconf/utils/boxing.py
            Update dynaconf/utils/boxing.py
            Add release script and CHANGELOG in place of history.

      Jaepil Koh (1):
            Update django.md

      Joel Perras (3):
            Allow dotted-path based setting of configuration key/value pairs.
            Handle nested includes in settings files.
            Remove extraneous lines.

      Mantas (3):
            Add INSTANCE_FOR_DYNACONF and --instance
            Remove mocker fixture
            Python 3.4 has different error message

      Matthias (1):
            Fix small typo in README.md

      mspinelli (2):
            fixed infinite recursion caused by copy()
            add tests for dynabox fix


1.2.0 (2018-11-30)
------------------
- Release version 1.2.0. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (6):
            Merge branch 'jperras-merge-multiple-settings-files'
            Merge branch 'master' of github.com:rochacbruno/dynaconf
            Fix #106 make PROJECT_ROOT_FOR_DYNACONF to work with custom paths
            Update dynaconf/utils/boxing.py
            Update dynaconf/utils/boxing.py
            Add release script and CHANGELOG in place of history.

      Jaepil Koh (1):
            Update django.md

      Joel Perras (3):
            Allow dotted-path based setting of configuration key/value pairs.
            Handle nested includes in settings files.
            Remove extraneous lines.

      Mantas (3):
            Add INSTANCE_FOR_DYNACONF and --instance
            Remove mocker fixture
            Python 3.4 has different error message

      Matthias (1):
            Fix small typo in README.md

      mspinelli (2):
            fixed infinite recursion caused by copy()
            add tests for dynabox fix
- Add release script and CHANGELOG in place of history. [Bruno Rocha]
- Add tests for dynabox fix. [mspinelli]
- Update dynaconf/utils/boxing.py. [Bruno Rocha, mspinelli]
- Update dynaconf/utils/boxing.py. [Bruno Rocha, mspinelli]
- Fixed infinite recursion caused by copy() [mspinelli]
- Fix #106 make PROJECT_ROOT_FOR_DYNACONF to work with custom paths.
  [Bruno Rocha]

  Added example/project_root and entry on Makefile:test_examples
- Update django.md. [Jaepil Koh]

  Typo!
- Fix small typo in README.md. [Matthias]
- Merge branch 'master' of github.com:rochacbruno/dynaconf. [Bruno
  Rocha]
- Python 3.4 has different error message. [Mantas]
- Remove mocker fixture. [Mantas]

  Left this accidentaly.

  https://travis-ci.org/rochacbruno/dynaconf/jobs/452612532
- Add INSTANCE_FOR_DYNACONF and --instance. [Mantas]

  There parameters allows dynaconf to use different LazySettings instance
  if project uses one.

  Also did some other fixes along the way:

  - Added `catch_exceptions=False` to `CliRunner.invoke` in order to
    prevent click from swallowing errors silently. This uncovered other
    errors in init and validate cli commands.

  - Removed module level code execution from cli module. Module level code
    execution makes it really difficult to test code. Now cli does not
    rely on global state and can be tested properly.

  - Removed a code snipper from LazySettings which modified global
    default_settings values. This means, that each LazySettings
    constructor call has side effects.

  - `dynaconf validate` command tests were useless because they didn't
    test anything and I found, that `dynaconf validate` command don't even
    work and raises ValidationError if there are any validation errors.
    Changed that to cli friendly error message.
- Merge branch 'jperras-merge-multiple-settings-files' [Bruno Rocha]
- Remove extraneous lines. [Joel Perras]
- Handle nested includes in settings files. [Joel Perras]

  A settings file can include a `dynaconf_include` stanza, whose exact
  syntax will depend on the type of settings file (json, yaml, toml, etc)
  being used:

  ```toml
  [default]
  dynaconf_include = ["/absolute/path/to/plugin1.toml", "relative/path/to/plugin2.toml"]
  DEBUG = false
  SERVER = "www.example.com"
  ```

  When loaded, the files located at the (relative or absolute) paths in
  the `dynaconf_include` key will be parsed, in order, and override any
  base settings that may exist in your current configuration.

  The paths can be relative to the base `settings.(toml|yaml|json|ini|py)`
  file, or can be absolute paths.

  The idea here is that plugins or extensions for whatever framework or
  architecture you are using can provide their own configuration values
  when necessary.

  It is also possible to specify glob-based patterns:

  ```toml
  [default]
  dynaconf_include = ["configurations/*.toml"]
  DEBUG = false
  SERVER = "www.example.com"
  ```

  Currently, only a single level of includes is permitted to keep things
  simple and straightforward.
- Allow dotted-path based setting of configuration key/value pairs.
  [Joel Perras]

  You can set a value with an arbitrary number of nested keys, separated
  by dots:

  ```python
  settings.set('nested_1.nested_2.nested_3.nested_4', 'secret')
  ```

  And accessing the keys/values with dotted-path lookup behaves as
  expected:

  ```python
  print(settings.NESTED_1.NESTED_2.NESTED_3.to_dict())
  ```

  If for some reason you didn't want to have a key parsed into nested
  structures delimited by dots and just wanted a key of "foo.bar", you can
  disable the parsing with:

  ```python
  settings.set('nested_1.nested_2.nested_3.nested_4',
               'secret',
               dotted_lookup=False)
  ```

  And accessing keys that don't exist will raise `KeyError`:

  ```python
  settings.NESTED_1.NESTED_5
  ```


1.1.0 (2018-10-26)
------------------
- Released 1.1.0. [Bruno Rocha]

  - Added `MERGE_ENABLED_FOR_DYNACONF` with ability to merge nested dictionaries instead of replacing PR #88
  - Support for dot notation to access nested dictionaries like `settings['KEY.OTHER.NESTED.DEEPER']` PR #93
  - Support dotted notation for validators PR #98
  - Fixed a bug in SETTINGS_MODULE cleanup when `.setenv` method was called PR #97
  - Added Python 3.7 to test matrix PR #99
- Fixing new flake8 warnings. [Bruno Rocha]
- Update py.test command in tox to allow passing positional arguments.
  [Joel Perras]

  The basic, default functionality of running `tox` remains unchanged. You
  are now, however, able to pass positional arguments to `py.test` at
  invocation time. For example:

  ```bash
  tox -- -x --pdb tests/test_basic.py
  ```

  Which will pass all input after the `--` separator (which is used to
  signify the end of possible options to `tox`) down to the `py.test`
  command in the `{posargs}` location, as defined in `tox.ini`.
- Enable Python 3.7 env for tox testing. [Joel Perras]
- Enable python 3.7 in TravisCI config. [Joel Perras]
- Updates Missing singleton with __eq__ dunder. (#98) [Joël Perras]

  Adds some additional tests for the `Missing` class and singleton
  instance usage to ensure it returns equality only for comparisons to
  itself and not `None`, or `False`, or `True`.
- Merge branch 'jperras-dotted-validators' [Bruno Rocha]
- Updates Missing singleton with __eq__ dunder. [Joel Perras]

  Adds some additional tests for the `Missing` class and singleton
  instance usage to ensure it returns equality only for comparisons to
  itself and not `None`, or `False`, or `True`.
- Implements dotted-path validator name declarations. [Joel Perras]

  One is now able to write:

  ```python
  settings.validators.register(
      Validator('REDIS',  must_exist=True,  is_type_of=dict),
      Validator('REDIS.HOST', must_exist=True, is_type_of=str),
      Validator('REDIS.PORT', must_exist=True, is_type_of=int),
  )
  ```

  Which will validate the dotted attributes as nested structures. For
  example, in yaml:

  ```yaml
  DEFAULT:
      REDIS:
          HOST: localhost
          PORT: 1234
  ```

  This necessitated a slight but non-negligible change in the
  implementation of `Settings.exists()`, which previously did a shallow
  check of loaded data. It has now been updated to perform a
  `Settings.get()` of the key in question, and compares that to a newly
  defined sentinel value to ensure `None` values do not cause a false
  negative result.

  New tests and assertions have been added to cover the new functionality.
  Docs have been updated to show an example of the nested validator name
  definition in action.

  Closes rochacbruno/dynaconf#85.
- Fix #94 setenv cleans SETTINGS_MODULE attribute. [Bruno Rocha]
- Merge branch 'jperras-dot-traversal-access' [Bruno Rocha]
- Merge branch 'dot-traversal-access' of
  https://github.com/jperras/dynaconf into jperras-dot-traversal-access.
  [Bruno Rocha]
- Allow dot-traversal access to nested dictionaries. [Joel Perras]

  A simple memoized recursion has been added to `get()` if the key
  contains at least one dot.

  The caller can choose to opt-out of this behaviour by specifying the
  `dotted_lookup` argument:

  ```python
  settings('AUTH.USERNAME', dotted_lookup=False)
  ```

  While the performance impact of this has not been quantified, the net
  impact in any real-world application should be minimal due to typical
  nesting levels, and the fact that we overwrite the memoized portion of
  the dotted-key lookup on each iteration.

  - Avoids regressions [✓]
  - Can be opted-out on a per-call basis [✓]
  - Minimal performance impact [✓]
  - Documented [✓]
  - Tested [✓]
  - Examples added [✓]

  Closes rochacbruno/dynaconf#84
- Merge branch 'rsnyman-merge-settings' [Bruno Rocha]
- Add example for merge_configs. [Bruno Rocha]
- Add setting merging. [Raoul Snyman]

  - Addd the ability to merge nested structures instead of completely overwriting them
  - Use monkeypatch to stop one test from interferring with another
  - Updated documentation


1.0.6 (2018-09-13)
------------------
- Release 1.0.6. [Bruno Rocha]

  Fixed issue #81 -  added ENCODING_FOR_DYNACONF to handle different settings files encodings specially on Windows
- Add ENCODING_FOR_DYNACONF to handle different file encoding Fix #81.
  [Bruno Rocha]

  By default ENCODING_FOR_DYNACONF is utf-8 (recommended to always write settings files in utf-8)
  If you need to change the format of settings file set the variable:

  ```
  export ENCODING_FOR_DYNACONF="cp1252"
  ```


1.0.5 (2018-09-07)
------------------
- Bump dev version. [Bruno Rocha]
- Added few more enhancements to django and flask extensions + docs.
  [Bruno Rocha]
- Bump dev version. [Bruno Rocha]


1.0.4 (2018-09-07)
------------------
- Fix the definition of Django prefixed variable. [Bruno Rocha]
- Merge pull request #78 from mattkatz/patch-1. [Bruno Rocha]

  small corrections for usage.md
- Small corrections for usage.md. [Matt Katz]

  This library is great, just a correction in the docs.

  There must be AT LEAST one default section.

  Changed **ATTENTION** to **ATTENTION**: to match with the style of **NOTE:**
- Merge pull request #75 from yoyonel/master. [Bruno Rocha]

  Fix in 'dynaconf/base.py' for __getitem__ method
- Bump version. [latty]
- [Fix] in 'dynaconf/base.py' for __getitem__ method, change (fix) the
  condition to raise a exception. Update unit tests. Bump version.
  [latty]
- Release 1.0.3. [Bruno Rocha]

  - Excluded example and tests from realease dist
  - removed root logger configuration


1.0.3 (2018-06-26)
------------------
- Merge pull request #72 from chobeat/issue_71. [Bruno Rocha]

  Removed root config
- Removed root config. [Simone Robutti]
- Merge pull request #70 from allan-silva/master. [Bruno Rocha]

  Exclude example and tests folders from setup (twitter help wanted)
- Exclude example and tests folders from setup (twitter help wanted)
  [allan.silva]
- Merge pull request #67 from cassiobotaro/patch-1. [Bruno Rocha]

  Incorrect help
- Fix docs. [cassiobotaro]
- Incorrect help. [Cássio Botaro]

  For while is impossible to use --to as argument.
- Merge pull request #66 from gpkc/patch-1. [Bruno Rocha]

  Fixing typos
- Merge pull request #1 from gpkc/patch-2. [Guilherme Caminha]

  Update README.md
- Update README.md. [Guilherme Caminha]
- Update usage.md. [Guilherme Caminha]
- Adjust logs to include python module names. [Bruno Rocha]
- Fix sphinx aafig syntax for python 3.x. [Bruno Rocha]


1.0.2 (2018-05-31)
------------------
- Merge pull request #65 from rochacbruno/testing_bare_install. [Bruno
  Rocha]

  Add install test stage
- Add -y. [Bruno Rocha]
- Add install test stage. [Bruno Rocha]
- Fix loader import error and improved logs. [Bruno Rocha]
- Clean up [skip ci] [Bruno Rocha]
- Fix URL generation in markdown for sphinx [skip ci] [Bruno Rocha]
- Merge pull request #64 from rochacbruno/improve_docs. [Bruno Rocha]

  Improved documentation
- Improved documentation. [Bruno Rocha]
- [skip ci] [Bruno Rocha]


1.0.1 (2018-05-30)
------------------
- Merge pull request #63 from rochacbruno/adds_more_python_versions.
  [Bruno Rocha]

  Adds more python versions
- Cover. [Bruno Rocha]
- Cover. [Bruno Rocha]
- Skip 3.7-dev. [Bruno Rocha]
- More trabis build stages. [Bruno Rocha]
- Add missing .env. [Bruno Rocha]
- Fix #60 CLI validator command. [Bruno Rocha]
- Fix #59 cli commands working for Flask and Django apps. [Bruno Rocha]
- Fixes to support Python 3.4, 3.5 and 3.6 Fix #62. [Bruno Rocha]
- Strict use of _FOR_DYNACONF envvars. [Bruno Rocha]
- Aafigure. [Bruno Rocha]
- Pinned docutils. [Bruno Rocha]
- Rtfd fix. [Bruno Rocha]
- Add rtfd yml. [Bruno Rocha]
- Added init file to docs. [Bruno Rocha]
- Add import path. [Bruno Rocha]
- Docs. [Bruno Rocha]
- Finished README with all the new implementations. [Bruno Rocha]


1.0.0 (2018-05-28)
------------------
- Merge pull request #56 from
  rochacbruno/all_the_namespace_changed_to_env. [Bruno Rocha]

  Major Breaking Refactor related to #54
- Travis fix 2. [Bruno Rocha]
- Travis global fix. [Bruno Rocha]
- Travis fix for new style toml envvars. [Bruno Rocha]
- Deprecated `@type` casting in favor of TOML syntax, rewriting readme.
  [Bruno Rocha]
- Add `settings.flag` [Bruno Rocha]
- Using `dynaconf write` in test_redis|vault. [Bruno Rocha]
- Added `dynaconf --docs` [Bruno Rocha]
- Added `dynaconf --version` [Bruno Rocha]
- Removed transformators. [Bruno Rocha]
- 100% coverage for validators. [Bruno Rocha]
- Increase cli test coverage. [Bruno Rocha]
- Dynaconf variables in blue and user variables in green. [Bruno Rocha]
- Added `dynaconf list` and `dynaconf write` subcommands. [Bruno Rocha]
- More cli commands lsit and write. [Bruno Rocha]
- Added more tests for cli and py loader. [Bruno Rocha]
- Replaced coveralls with codecov #57. [Bruno Rocha]
- Modularized the loaders, added `dynaconf init` command. [Bruno Rocha]
- As environment variable the only prefix allowed is the GLOBAL_ENV..
  default to DYNACONF_ [Bruno Rocha]
- Added more examples/tests and test_cli. [Bruno Rocha]
- Removed cleaners. [Bruno Rocha]
- Major Breaking Refactor related to #54. [Bruno Rocha]


0.7.6 (2018-05-21)
------------------
- Merge pull request #52 from rochacbruno/fix_namespace_in_django.
  [Bruno Rocha]

  Fix namespace swithc in django apps
- Add missing .env. [Bruno Rocha]
- Fix namespace swithc in django apps. [Bruno Rocha]


0.7.5 (2018-05-20)
------------------
- Merge pull request #51 from rochacbruno/added_django_extension. [Bruno
  Rocha]

  Added django extension
- 0.7.5 release with Django extension (experimental) [Bruno Rocha]
- Dont commit dbs. [Bruno Rocha]
- Added Django extension tests and example app. [Bruno Rocha]
- Added Django extension. [Bruno Rocha]


0.7.4 (2018-05-19)
------------------
- Merge pull request #50 from rochacbruno/074. [Bruno Rocha]

  Fix precedence of namespace in loaders
- Fix precedence of namespace in loaders. [Bruno Rocha]
- Merge pull request #49 from thekashifmalik/patch-1. [Bruno Rocha]

  Fix typo in README.
- Fix typo in README. [Kashif Malik]
- HOTFIX: redis config. [Bruno Rocha]
- Merge pull request #48 from rochacbruno/redis_tests. [Bruno Rocha]

  Added tests for Redis loader
- Added tests for Redis loader. [Bruno Rocha]
- Merge pull request #47 from rochacbruno/vault_tests. [Bruno Rocha]

  Added test for vaultproject
- Fix deadlock in vault writer. [Bruno Rocha]
- Added test for vaultproject. [Bruno Rocha]


0.7.3 (2018-05-13)
------------------
- Merge pull request #45 from rochacbruno/vault_loader. [Bruno Rocha]

  Added support for vaultproject (hashi corp) loader
- Added README section. [Bruno Rocha]
- Added note to readme. [Bruno Rocha]
- Added tests. [Bruno Rocha]
- Fixing for python-box 3.2.0. [Bruno Rocha]
- Added config AUTO_CAST_FOR_DYNACONF=off|0|disabled|false Suggested by
  @danilobellini. [Bruno Rocha]
- Fixed env variable for debug level in README.md. [Simone Robutti]
- Implementation of Vault loader. [Bruno Rocha]
- Vaultproject loader implementation. [Bruno Rocha]
- Merge pull request #46 from rochacbruno/disable_cast. [Bruno Rocha]

  Added config AUTO_CAST_FOR_DYNACONF=off|0|disabled|false
- Added note to readme. [Bruno Rocha]
- Added tests. [Bruno Rocha]
- Fixing for python-box 3.2.0. [Bruno Rocha]
- Added config AUTO_CAST_FOR_DYNACONF=off|0|disabled|false Suggested by
  @danilobellini. [Bruno Rocha]
- Merge pull request #44 from chobeat/patch-1. [Bruno Rocha]

  Fixed env variable for debug level in README.md
- Fixed env variable for debug level in README.md. [Simone Robutti]


0.7.2 (2018-05-07)
------------------
- Added test for compat. [Bruno Rocha]
- Added SETTINGS_MODULE to SETTINGS_MODULE_FOR_DYNACONF in compat.
  [Bruno Rocha]
- Added backwards compatibility for old style kwargs. [Bruno Rocha]
- Merge pull request #30 from vladcalin/add-docs. [Bruno Rocha]

  Add docs skeleton with autogenerated module docs
- Add docs skeleton with autogenerated module docs. [Vlad Calin]


0.7.0 (2018-05-07)
------------------
- README updates [ci skip] [Bruno Rocha]
- Added support for `.secrets` files. [Bruno Rocha]
- Merge pull request #43 from rochacbruno/test_coverage. [Bruno Rocha]

  Adjusting ENVVARS names and better test coverage
- Travis testing. [Bruno Rocha]
- Adjust travis.yml for muultiple jobs. [Bruno Rocha]
- Never cleans default keys. [Bruno Rocha]
- Refactoring for better test cov. [Bruno Rocha]
- Adjusting ENVVARS names and better test coverage. [Bruno Rocha]


0.6.0 (2018-05-04)
------------------
- Release of 0.6.0. [Bruno Rocha]
- Merge pull request #42 from rochacbruno/fix41. [Bruno Rocha]

  Fix #41
- Fix #41. [Bruno Rocha]
- Merge pull request #40 from rochacbruno/inifiles. [Bruno Rocha]

  ini and json files + parseconf recursive and find_file function
- Ini and json files + parseconf recursive and find_file function.
  [Bruno Rocha]

  - Added support for .ini and .json files
  - parse conf is now recursive to parse dict inner data
  - Cloned find_file function from dotenv
- Merge pull request #38 from rochacbruno/flask_dot_env. [Bruno Rocha]

  Added Flask 1.0 dotenv support
- IMplemented TOML loader. [Bruno Rocha]
- Adjusted MARKDOWN. [Bruno Rocha]
- Added Flask 1.0 dotenv support. [Bruno Rocha]


0.5.2 (2017-10-03)
------------------
- Small fix on 0.5.2 :hamster: [Bruno Rocha]
- 0.5.1 with YAML hotfixes and allowing multiple yaml files. [Bruno
  Rocha]


0.5.0 (2017-09-26)
------------------
- Drop 3.4 and 3.5. [Bruno Rocha]
- Silent errors on YAML missing namespace by default. [Bruno Rocha]
- Update README.md. [Bruno Rocha]
- Update README.md. [Bruno Rocha]
- Merge branch 'Sytten-expand-yaml-config' [Bruno Rocha]
- Specialized Box as Dynabox to allow upper and lower case access.
  [Bruno Rocha]
- Use box. [Emile Fugulin]
- Add expanded object for yaml. [Emile Fugulin]


0.4.5 (2017-05-30)
------------------
- Update README.md. [Bruno Rocha]
- Update README.md. [Bruno Rocha]
- Update README.md. [Bruno Rocha]
- Merge pull request #20 from douglas/master. [Bruno Rocha]

  Upgrade dynaconf to 0.4.5 =)
- Upgrade dynaconf to 0.4.5 =) [Douglas Soares de Andrade]
- Improves the way Tox installs the projects dependencies. [Douglas
  Soares de Andrade]
- Make tests directory a package. [Douglas Soares de Andrade]

  - So we can use the syntax from dynaconf import …
- Make it clear where we are getting LazySettings from. [Douglas Soares
  de Andrade]
- Add m2r and Flask to Pipenv. [Douglas Soares de Andrade]
- Removing pdbpp as it breaks with Python 3.3. [Douglas Soares de
  Andrade]
- Update readme. [Bruno Rocha]
- Update README. [Bruno Rocha]


0.4.4 (2017-03-21)
------------------
- HOTFIX: Flask templates always expects `None` for KeyError or
  AttrError. [Bruno Rocha]
- Bump version. [Bruno Rocha]
- Update README.md. [Bruno Rocha]
- Added FlaskDynaconf to readme. [Bruno Rocha]
- Merge pull request #16 from rochacbruno/added_flaskdynaconf. [Bruno
  Rocha]

  Added FlaskDynaconf
- Added FlaskDynaconf. [Bruno Rocha]
- Update README.md. [Bruno Rocha]
- Merge pull request #15 from douglas/master. [Bruno Rocha]

  Make the project work both on Python2 and Python3
- PEP8/Pylint and fixes equality operators. [Douglas Soares de Andrade]
- Remove unused code. [Douglas Soares de Andrade]
- PEP8 and Pylint fixes. [Douglas Soares de Andrade]
- Remove pypy3 as it does not work. [Douglas Soares de Andrade]
- Adding pypy and pypy3 to Travis. [Douglas Soares de Andrade]
- Oops, need to rename _super to super. [Douglas Soares de Andrade]
- Fix the import according to pep8. [Douglas Soares de Andrade]
- Remove this to see if it is still an issue. [Douglas Soares de
  Andrade]
- Adding Python 2.7. [Douglas Soares de Andrade]
- Adding the editorconfig file. [Douglas Soares de Andrade]
- Add Pipfile.lock to .gitignore. [Douglas Soares de Andrade]
- Small Refactory. [Douglas Soares de Andrade]

  - Adding object to the Settings classe to make it work with Python2
- Small Refactory. [Douglas Soares de Andrade]

  - Reordering the imports according to  pylint and flake8
  - Adding object to the classes to make them work with Python2
- Small Refactory. [Douglas Soares de Andrade]

  - Fixing the __init__ signature to make it compatible with python2 and
  python3
  - Adding object to the class to make Python2 work
- Adding the Pipenv file. [Douglas Soares de Andrade]

  - To allow us to use: https://github.com/kennethreitz/pipenv
- Adding Tox to helps us test the library. [Douglas Soares de Andrade]
- Fix #14 casting bool for booleans tks to @dbstraffin. [Bruno Rocha]
- Fix yaml cleaner, renamed `defined` to `must_exist` in validator.
  [Bruno Rocha]
- Added validators. [Bruno Rocha]


0.4.1 (2017-02-12)
------------------
- Bump 0.4.1. [Bruno Rocha]
- Merge pull request #13 from rochacbruno/add_yaml_support. [Bruno
  Rocha]

  Added YAML support
- Added YAML support. [Bruno Rocha]
- Force pip upgrade in travis. [Bruno Rocha]
- Drop support to Python 2.x - #MoveToPython3 Now! [Bruno Rocha]
- Add 'decode_responses': True note. [Bruno Rocha]
- Fix travis error. [Bruno Rocha]
- Python 3 support. [Bruno Rocha]
- Update README.md. [Bruno Rocha]


0.3.0 (2016-01-14)
------------------
- Fix error when envvar key has leading or trailing spaces. [Bruno
  Rocha]
- Pip released. [Bruno Rocha]
- Pypi is in troublr to release. [Bruno Rocha]
- Bump. [Bruno Rocha]
- If 'settings.py' is found on PROJECT_ROOT it is read. [Bruno Rocha]
- Make release. [Bruno Rocha]
- Path_for returns rooted path if starts with / [Bruno Rocha]
- Added settings.path_for. [Bruno Rocha]
- Ignore functional styling smells. [Bruno Rocha]
- Update README.md. [Bruno Rocha]
- Travis envvars matrix. [Bruno Rocha]
- Update .travis.yml. [Bruno Rocha]
- Starting to write tests :) [Bruno Rocha]
- Simplified objects, removed UserSettings, removed exceptions. [Bruno
  Rocha]


0.2.7 (2015-12-23)
------------------
- Removed six and used obj.set. [Bruno Rocha]
- Update README.md. [Bruno Rocha]
- Added png. [Bruno Rocha]
- Redis loader uses hash. [Bruno Rocha]
- Using HASH to store data, added always_fresh vars and context thanks
  to @dmoliveira and @ederfmartins. [Bruno Rocha]
- Added settings_module as cached property. [Bruno Rocha]
- Added delete function to redis_writer. [Bruno Rocha]
- Added note about get_fresh in readme. [Bruno Rocha]
- Better namespace management, get_fresh(key) to access redis. [Bruno
  Rocha]
- Now it can be used programatically. [Bruno Rocha]


0.2.1 (2015-12-20)
------------------
- Added redis_writer. [Bruno Rocha]
- Update readme. [Bruno Rocha]


0.2.0 (2015-12-20)
------------------
- Can also load from arbitraty filepath. [Bruno Rocha]
- Renamed var, added loaders, bump version. [Bruno Rocha]


0.1.2 (2015-08-20)
------------------
- Format on readme. [Bruno Rocha]
- More casting options. [Bruno Rocha]
- Fix #1 multiple namespaces. [Bruno Rocha]
- Update README.md. [Bruno Rocha]
- Update README.md. [Bruno Rocha]
- Update README.md. [Bruno Rocha]
- Added default. [Bruno Rocha]
- Initial commit. [Bruno Rocha]
