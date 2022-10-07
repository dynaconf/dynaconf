Changelog
=========


3.1.11 (2022-09-22)
-------------------
- Release version 3.1.11. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (2):
            Release version 3.1.10
            Release hotfix (no need to run coverage or include tests_functional)
- Release hotfix (no need to run coverage or include tests_functional)
  [Bruno Rocha]
- Release version 3.1.10. [Bruno Rocha]

  Shortlog of commits since last release:

      Amadou Crookes (1):
            envars.md typo fix (#786)

      Bruno Rocha (19):
            Release version 3.1.9
            Bump dev version to 3.1.10
            Update badges
            demo repo will be replaced by a video tutorial soon
            Fix CI
            New data key casing must adapt to existing key casing (#795)
            Add test and docs about includes (#796)
            Removed vendor_src folder (#798)
            Replacing rochacbruno/ with dynaconf/ (#800)
            Fix codecov (#801)
            Parse negative numbers from envvar Fix #799 and Fix #585 (#802)
            Fix get command with Django (#804)
            Add a functional test runner (#805)
            Test runner docs and styling (#806)
            Allow merge_unique on lists when merge_enabled=True (#810)
            Rebind current env when forced for Pytest Fix #728 (#809)
            AUTO_CAST can be enabled on instance (#811)
            Ensure pyminify is on release script
            Add missing tomllib to monify script

      Gaurav Talreja (1):
            Fix #807 Use client.auth.approle.login instead of client.auth_approle (#808)

      Jitendra Yejare (1):
            Fix #768 of kv property depreciation from client object (#769)

      Joren Retel (2):
            Feature/detect casting comb token from converters (#784)
            Adding documentation and example to makefile. (#791)

      João Gustavo A. Amorim (1):
            Add pyupgrade hook (#759)

      Kian-Meng Ang (1):
            Fix typos (#788)

      Lucas Limeira (1):
            Using filter_strategy in env_loader to fix #760 (#767)

      Nicholas Nadeau, Ph.D., P.Eng (1):
            fix: typo (#766)

      Oleksii Baranov (2):
            Bump codecov action version (#775)
            Fix cli init command for flask (#705) (#774)

      Pedro de Medeiros (1):
            documentation fixes (#771)

      The Gitter Badger (1):
            Add a Gitter chat badge to README.md (#776)

      Théo Melo (1):
            Fixing a typo on the readme file (#763)

      Vicente Marçal (1):
            docs(pt-br): Docs Translation to brazilian portugues. (#787)


3.1.10 (2022-09-22)
-------------------

Fix
~~~
- Typo (#766) [Bruno Rocha, Nicholas Nadeau, Ph.D., P.Eng]

Other
~~~~~
- Release version 3.1.10. [Bruno Rocha]

  Shortlog of commits since last release:

      Amadou Crookes (1):
            envars.md typo fix (#786)

      Bruno Rocha (19):
            Release version 3.1.9
            Bump dev version to 3.1.10
            Update badges
            demo repo will be replaced by a video tutorial soon
            Fix CI
            New data key casing must adapt to existing key casing (#795)
            Add test and docs about includes (#796)
            Removed vendor_src folder (#798)
            Replacing rochacbruno/ with dynaconf/ (#800)
            Fix codecov (#801)
            Parse negative numbers from envvar Fix #799 and Fix #585 (#802)
            Fix get command with Django (#804)
            Add a functional test runner (#805)
            Test runner docs and styling (#806)
            Allow merge_unique on lists when merge_enabled=True (#810)
            Rebind current env when forced for Pytest Fix #728 (#809)
            AUTO_CAST can be enabled on instance (#811)
            Ensure pyminify is on release script
            Add missing tomllib to monify script

      Gaurav Talreja (1):
            Fix #807 Use client.auth.approle.login instead of client.auth_approle (#808)

      Jitendra Yejare (1):
            Fix #768 of kv property depreciation from client object (#769)

      Joren Retel (2):
            Feature/detect casting comb token from converters (#784)
            Adding documentation and example to makefile. (#791)

      João Gustavo A. Amorim (1):
            Add pyupgrade hook (#759)

      Kian-Meng Ang (1):
            Fix typos (#788)

      Lucas Limeira (1):
            Using filter_strategy in env_loader to fix #760 (#767)

      Nicholas Nadeau, Ph.D., P.Eng (1):
            fix: typo (#766)

      Oleksii Baranov (2):
            Bump codecov action version (#775)
            Fix cli init command for flask (#705) (#774)

      Pedro de Medeiros (1):
            documentation fixes (#771)

      The Gitter Badger (1):
            Add a Gitter chat badge to README.md (#776)

      Théo Melo (1):
            Fixing a typo on the readme file (#763)

      Vicente Marçal (1):
            docs(pt-br): Docs Translation to brazilian portugues. (#787)
- Add missing tomllib to monify script. [Bruno Rocha]
- Ensure pyminify is on release script. [Bruno Rocha]
- AUTO_CAST can be enabled on instance (#811) [Bruno Rocha]

  Fix #772
- Rebind current env when forced for Pytest Fix #728 (#809) [Bruno
  Rocha]
- Allow merge_unique on lists when merge_enabled=True (#810) [Bruno
  Rocha]

  Fix #726
- Fix #807 Use client.auth.approle.login instead of client.auth_approle
  (#808) [Gaurav Talreja]
- Fix typos (#788) [Kian-Meng Ang]

  Found via this command:

      codespell -S "./dynaconf/vendor/*,./docs/pt-br/*,./.mypy_cache/*,*.svg" -L hashi
- Test runner docs and styling (#806) [Bruno Rocha]

  * Test runner docs and styling

  * No emojis on windows
- Add a functional test runner (#805) [Bruno Rocha]

  * Add a functional test runner

  * Renamed example/ to tests_functional/
- Fix get command with Django (#804) [Bruno Rocha]

  Fix #789
- Parse negative numbers from envvar Fix #799 and Fix #585 (#802) [Bruno
  Rocha]
- Fix codecov (#801) [Bruno Rocha]

  * Fix codecov

  * call coverage xml
- Replacing rochacbruno/ with dynaconf/ (#800) [Bruno Rocha]

  * Replacing rochacbruno/ with dynaconf/

  * xscode doesn't exist anymore
- Removed vendor_src folder (#798) [Bruno Rocha]

  * Removed vendor_src folder

  Now `vendor` is the source
  and minification happens during release process.

  * Added tomllib (vendored) as a replacement for toml fix #708

  toml kept as a fallback until 4.0.0 to nor break compatibility

  - toml follows 0.5.0 spec
  - tomlib follows 1.0.0 spec
  - toml allows emojis and unicode chars unencoded
  - tomllib foolows the spec where only encoded chars are allowed
- Add test and docs about includes (#796) [Bruno Rocha]

  closes #794
- New data key casing must adapt to existing key casing (#795) [Bruno
  Rocha]

  Fix #737
- Docs(pt-br): Docs Translation to brazilian portugues. (#787) [Vicente
  Marçal]
- Adding documentation and example to makefile. (#791) [Joren Retel]

  * Adding documentation and example to makefile.

  * Put header one level down in  docs.
- Feature/detect casting comb token from converters (#784) [Joren Retel]
- Envars.md typo fix (#786) [Amadou Crookes]
- Fix CI. [Bruno Rocha]
- Demo repo will be replaced by a video tutorial soon. [Bruno Rocha]
- Update badges. [Bruno Rocha]
- Documentation fixes (#771) [Bruno Rocha, Pedro de Medeiros]
- Add a Gitter chat badge to README.md (#776) [Bruno Rocha, The Gitter
  Badger]
- Fix cli init command for flask (#705) (#774) [Bruno Rocha, Oleksii
  Baranov]
- Bump codecov action version (#775) [Oleksii Baranov]
- Fix #768 of kv property depreciation from client object (#769)
  [Jitendra Yejare]
- Using filter_strategy in env_loader to fix #760 (#767) [Lucas Limeira]
- Fixing a typo on the readme file (#763) [Théo Melo]
- Add pyupgrade hook (#759) [João Gustavo A. Amorim]

  * update hooks and add pyupgrade

  * updates by pyupgrade

  * remove unused typing imports

  * add `from __future__ import annotations` across the codebase

  * add `from __future__ import annotations` in examples
- Bump dev version to 3.1.10. [Bruno Rocha]
- Release version 3.1.9. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (4):
            Release version 3.1.8
            Bye py 3.7
            Multiple fixes for 3.19 (#756)
            update docs site (#758)

      João Gustavo A. Amorim (1):
            Organize pre-commit setup (#757)

      dependabot[bot] (1):
            Bump django from 2.2.27 to 2.2.28 in /example/django_pytest_pure (#743)


3.1.9 (2022-06-06)
------------------
- Release version 3.1.9. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (4):
            Release version 3.1.8
            Bye py 3.7
            Multiple fixes for 3.19 (#756)
            update docs site (#758)

      João Gustavo A. Amorim (1):
            Organize pre-commit setup (#757)

      dependabot[bot] (1):
            Bump django from 2.2.27 to 2.2.28 in /example/django_pytest_pure (#743)
- Update docs site (#758) [Bruno Rocha]
- Organize pre-commit setup (#757) [João Gustavo A. Amorim]
- Multiple fixes for 3.19 (#756) [Bruno Rocha]
- Bump django from 2.2.27 to 2.2.28 in /example/django_pytest_pure
  (#743) [dependabot[bot], dependabot[bot]]
- Bye py 3.7. [Bruno Rocha]
- Release version 3.1.8. [Bruno Rocha]

  Shortlog of commits since last release:

      Anderson Sousa (1):
            Document the usage with python -m (#710)

      Andressa Cabistani (2):
            Add unique label when merging lists to fix issue #653 (#661)
            Add new validation to fix issue #585 (#667)

      Armin Berres (1):
            Fix typo in error message

      Bruno Rocha (7):
            Release version 3.1.7
            Found this bug that was duplicating the generated envlist (#663)
            Add support for Python 3.10 (#665)
            Attempt to fix #555 (#669)
            Create update_contributors.yml
            Fixing pre-coomit and docs CI
            Added `dynaconf get` command to cli (#730)

      Caneco (2):
            improvement: add brand new logo to the project (#686)
            improvement: update socialcard to match the python way (#687)

      EdwardCuiPeacock (2):
            Feature: add @jinja and @format casting (#704)
            Combo converter doc (#735)

      Eitan Mosenkis (1):
            Fix FlaskConfig.setdefault (#706)

      Enderson Menezes (Mr. Enderson) (2):
            Force PYTHONIOENCODING to utf-8 to fix #664 (#672)
            edit: move discussions to github tab (#682)

      Eugene Triguba (1):
            Fix custom prefix link in envvar documentation (#680)

      Gibran Herrera (1):
            Fix Issue 662 Lazy validation (#675)

      Jitendra Yejare (2):
            Load vault secrets from environment less stores or which are not written by dynaconf (#725)
            Use default value when settings is blank (#729)

      Pavel Alimpiev (1):
            Update docs link (#678)

      Ugo Benassayag (1):
            Added validate_only_current_env to validator (issue #734) (#736)

      Waylon Walker (1):
            Docs Fix Spelling (#696)

      dependabot[bot] (3):
            Bump django from 2.1.5 to 2.2.26 in /example/django_pytest_pure (#711)
            Bump mkdocs from 1.1.2 to 1.2.3 (#715)
            Bump django from 2.2.26 to 2.2.27 in /example/django_pytest_pure (#717)

      github-actions[bot] (2):
            [automated] Update Contributors File (#691)
            [automated] Update Contributors File (#732)

      lowercase00 (1):
            Makes Django/Flask kwargs case insensitive (#721)


3.1.8 (2022-04-15)
------------------
- Release version 3.1.8. [Bruno Rocha]

  Shortlog of commits since last release:

      Anderson Sousa (1):
            Document the usage with python -m (#710)

      Andressa Cabistani (2):
            Add unique label when merging lists to fix issue #653 (#661)
            Add new validation to fix issue #585 (#667)

      Armin Berres (1):
            Fix typo in error message

      Bruno Rocha (7):
            Release version 3.1.7
            Found this bug that was duplicating the generated envlist (#663)
            Add support for Python 3.10 (#665)
            Attempt to fix #555 (#669)
            Create update_contributors.yml
            Fixing pre-coomit and docs CI
            Added `dynaconf get` command to cli (#730)

      Caneco (2):
            improvement: add brand new logo to the project (#686)
            improvement: update socialcard to match the python way (#687)

      EdwardCuiPeacock (2):
            Feature: add @jinja and @format casting (#704)
            Combo converter doc (#735)

      Eitan Mosenkis (1):
            Fix FlaskConfig.setdefault (#706)

      Enderson Menezes (Mr. Enderson) (2):
            Force PYTHONIOENCODING to utf-8 to fix #664 (#672)
            edit: move discussions to github tab (#682)

      Eugene Triguba (1):
            Fix custom prefix link in envvar documentation (#680)

      Gibran Herrera (1):
            Fix Issue 662 Lazy validation (#675)

      Jitendra Yejare (2):
            Load vault secrets from environment less stores or which are not written by dynaconf (#725)
            Use default value when settings is blank (#729)

      Pavel Alimpiev (1):
            Update docs link (#678)

      Ugo Benassayag (1):
            Added validate_only_current_env to validator (issue #734) (#736)

      Waylon Walker (1):
            Docs Fix Spelling (#696)

      dependabot[bot] (3):
            Bump django from 2.1.5 to 2.2.26 in /example/django_pytest_pure (#711)
            Bump mkdocs from 1.1.2 to 1.2.3 (#715)
            Bump django from 2.2.26 to 2.2.27 in /example/django_pytest_pure (#717)

      github-actions[bot] (2):
            [automated] Update Contributors File (#691)
            [automated] Update Contributors File (#732)

      lowercase00 (1):
            Makes Django/Flask kwargs case insensitive (#721)
- Combo converter doc (#735) [EdwardCuiPeacock]
- Added validate_only_current_env to validator (issue #734) (#736) [Ugo
  Benassayag, Ugo Benassayag]
- [automated] Update Contributors File (#732) [github-actions[bot],
  rochacbruno]
- Added `dynaconf get` command to cli (#730) [Bruno Rocha]
- Fixing pre-coomit and docs CI. [Bruno Rocha]
- Fix typo in error message. [Armin Berres]

  It is, e.g., REDIS_HOST_FOR_DYNACONF - not REDIS_FOR_DYNACONF_HOST.
- Bump django from 2.2.26 to 2.2.27 in /example/django_pytest_pure
  (#717) [Bruno Rocha, dependabot[bot], dependabot[bot]]
- Bump mkdocs from 1.1.2 to 1.2.3 (#715) [Bruno Rocha, dependabot[bot],
  dependabot[bot]]
- Fix custom prefix link in envvar documentation (#680) [Andressa
  Cabistani, Bruno Rocha, Eugene Triguba]
- Use default value when settings is blank (#729) [Bruno Rocha, Jitendra
  Yejare]
- Load vault secrets from environment less stores or which are not
  written by dynaconf (#725) [Jitendra Yejare]
- Makes Django/Flask kwargs case insensitive (#721) [lowercase00]
- Docs Fix Spelling (#696) [Bruno Rocha, Waylon Walker]
- Bump django from 2.1.5 to 2.2.26 in /example/django_pytest_pure (#711)
  [Bruno Rocha, dependabot[bot], dependabot[bot]]
- [automated] Update Contributors File (#691) [github-actions[bot],
  rochacbruno]
- Feature: add @jinja and @format casting (#704) [Bruno Rocha,
  EdwardCuiPeacock]
- Document the usage with python -m (#710) [Anderson Sousa, Bruno Rocha]
- Fix FlaskConfig.setdefault (#706) [Eitan Mosenkis]
- Create update_contributors.yml. [Bruno Rocha]
- Improvement: update socialcard to match the python way (#687) [Caneco]
- Improvement: add brand new logo to the project (#686) [Caneco]
- Edit: move discussions to github tab (#682) [Enderson Menezes (Mr.
  Enderson)]
- Update docs link (#678) [Pavel Alimpiev]

  * Replace an old Django-related link with a new one

  * Update docs link
- Fix Issue 662 Lazy validation (#675) [Gibran Herrera]
- Force PYTHONIOENCODING to utf-8 to fix #664 (#672) [Enderson Menezes
  (Mr. Enderson)]
- Attempt to fix #555 (#669) [Bruno Rocha]
- Add new validation to fix issue #585 (#667) [Andressa Cabistani,
  andressa.cabistani]
- Add support for Python 3.10 (#665) [Bruno Rocha]

  Python 3.10 supported and tested
- Found this bug that was duplicating the generated envlist (#663)
  [Bruno Rocha]
- Add unique label when merging lists to fix issue #653 (#661) [Andressa
  Cabistani, andressa.cabistani]
- Release version 3.1.7. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (2):
            Release version 3.1.6
            Add missing docs and missing python_requires (#659)


3.1.7 (2021-09-09)
------------------
- Release version 3.1.7. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (2):
            Release version 3.1.6
            Add missing docs and missing python_requires (#659)
- Add missing docs and missing python_requires (#659) [Bruno Rocha]
- Release version 3.1.6. [Bruno Rocha]

  Shortlog of commits since last release:

      Ambient Lighter (1):
            Fix typo (#647)

      Bruno Rocha (19):
            Release version 3.1.4
            demo link (#546)
            removed release_notes from the docs. (#550)
            HOTFIX: Add coverage for 2 lines on validators.
            Fix #595 namedtuples are no more converted to BoxList (#623)
            Fix black issues (#631)
            Update FUNDING.yml
            description and type annotation for validator (#634)
            Add myoy and pre-commit to CI (#635)
            Update codaci badge (#636)
            Remove dependabot (this project has no dependencies)
            fix #596 django override (#645)
            fix #491 pytest django Fix #491 pytest and django (#646)
            Delete requirements.txt
            Update FUNDING.yml
            Add support for dynaconf_hooks(post) issue #654 (#655)
            Move to Github Actions (#656)
            Bye Azure (#657)
            Bump dev version

      FrankBattaglia (1):
            fix dict iterator methods for flask DynaconfConfig (#581)

      Jacob Callahan (1):
            Add the ability for selective validation (#549)

      Kamil Gałuszka (1):
            Add support for Python 3.9 and remove Ubuntu 16.04 that is deprecated in Azure Pipelines (#618)

      Konstantin (2):
            Update configuration.md (#553)
            Update configuration.md (#554)

      Linus Torvalds (1):
            Fix a typo in the docs

      Martin Thoma (1):
            Add type annotations for dynaconf.utils (#450)

      Nicholas Dentandt (1):
            feat: add filter strategy with PrefixFilter (#625)

      Robert Rosca (1):
            Add a warning if `--env` is passed to `init` (#629)

      Tanya Tereshchenko (1):
            Do not search anywhere if the absolute path to a file provided (#570)

      Yusuf Kaka (1):
            Added an example using FastAPI (#571)

      dependabot-preview[bot] (2):
            Bump mkdocs-material from 7.0.5 to 7.0.6 (#552)
            Upgrade to GitHub-native Dependabot (#574)

      puntonim (1):
            Fix typo (#588)


3.1.6 (2021-09-09)
------------------
- Release version 3.1.6. [Bruno Rocha]

  Shortlog of commits since last release:

      Ambient Lighter (1):
            Fix typo (#647)

      Bruno Rocha (19):
            Release version 3.1.4
            demo link (#546)
            removed release_notes from the docs. (#550)
            HOTFIX: Add coverage for 2 lines on validators.
            Fix #595 namedtuples are no more converted to BoxList (#623)
            Fix black issues (#631)
            Update FUNDING.yml
            description and type annotation for validator (#634)
            Add myoy and pre-commit to CI (#635)
            Update codaci badge (#636)
            Remove dependabot (this project has no dependencies)
            fix #596 django override (#645)
            fix #491 pytest django Fix #491 pytest and django (#646)
            Delete requirements.txt
            Update FUNDING.yml
            Add support for dynaconf_hooks(post) issue #654 (#655)
            Move to Github Actions (#656)
            Bye Azure (#657)
            Bump dev version

      FrankBattaglia (1):
            fix dict iterator methods for flask DynaconfConfig (#581)

      Jacob Callahan (1):
            Add the ability for selective validation (#549)

      Kamil Gałuszka (1):
            Add support for Python 3.9 and remove Ubuntu 16.04 that is deprecated in Azure Pipelines (#618)

      Konstantin (2):
            Update configuration.md (#553)
            Update configuration.md (#554)

      Linus Torvalds (1):
            Fix a typo in the docs

      Martin Thoma (1):
            Add type annotations for dynaconf.utils (#450)

      Nicholas Dentandt (1):
            feat: add filter strategy with PrefixFilter (#625)

      Robert Rosca (1):
            Add a warning if `--env` is passed to `init` (#629)

      Tanya Tereshchenko (1):
            Do not search anywhere if the absolute path to a file provided (#570)

      Yusuf Kaka (1):
            Added an example using FastAPI (#571)

      dependabot-preview[bot] (2):
            Bump mkdocs-material from 7.0.5 to 7.0.6 (#552)
            Upgrade to GitHub-native Dependabot (#574)

      puntonim (1):
            Fix typo (#588)
- Bump dev version. [Bruno Rocha]

  [skip ci]
- Bye Azure (#657) [Bruno Rocha]
- Move to Github Actions (#656) [Bruno Rocha]

  * Move to Github Actions

  - [ ] Codecov

  Fix #640

  * Enabled Vault and REdis
- Add support for dynaconf_hooks(post) issue #654 (#655) [Bruno Rocha]
- Update FUNDING.yml. [Bruno Rocha]
- Fix a typo in the docs. [Linus Torvalds]
- Fix typo (#647) [Ambient Lighter]
- Delete requirements.txt. [Bruno Rocha]
- Fix #491 pytest django Fix #491 pytest and django (#646) [Bruno Rocha]
- Fix #596 django override (#645) [Bruno Rocha]

  * Fix #596 django.test.override issue

  * Fix CI side effects
- Remove dependabot (this project has no dependencies) [Bruno Rocha]
- Update codaci badge (#636) [Bruno Rocha]
- Add myoy and pre-commit to CI (#635) [Bruno Rocha]
- Description and type annotation for validator (#634) [Bruno Rocha]
- Add a warning if `--env` is passed to `init` (#629) [Bruno Rocha,
  Bruno Rocha, Robert Rosca]

  * Add a warning if `--env` is passed to `init`

  * Fix typo, `file` was doubled in init help

  * Update docstrings for CLI

  * Raise error if using `-i` with `init` subcommand

  * Update docs to match current behaviour

  * add test coverage
- Add type annotations for dynaconf.utils (#450) [Bruno Rocha, Bruno
  Rocha, Martin Thoma]

  * Add type annotations for dynaconf.utils

  Make 'mypy .' succeed; to a big extend by ignoring errors

  * Manually format line length

  * Drop Python 3.6

  * Coverage fix
- Do not search anywhere if the absolute path to a file provided (#570)
  [Bruno Rocha, Tanya Tereshchenko]

  * Do not search anywhere if the absolute path to a file provided

  fixes #569

  * Fix test coverage and added some comments.
- Update FUNDING.yml. [Bruno Rocha]
- Fix black issues (#631) [Bruno Rocha]
- Feat: add filter strategy with PrefixFilter (#625) [Nicholas Dentandt]
- Fix typo (#588) [Bruno Rocha, puntonim]
- Added an example using FastAPI (#571) [Bruno Rocha, Yusuf Kaka]
- Fix dict iterator methods for flask DynaconfConfig (#581) [Bruno
  Rocha, Frank Battaglia, FrankBattaglia]
- Fix #595 namedtuples are no more converted to BoxList (#623) [Bruno
  Rocha]
- Add support for Python 3.9 and remove Ubuntu 16.04 that is deprecated
  in Azure Pipelines (#618) [Kamil Gałuszka]
- Upgrade to GitHub-native Dependabot (#574) [dependabot-preview[bot],
  dependabot-preview[bot]]
- Update configuration.md (#554) [Bruno Rocha, Konstantin]

  Remove redundant `s` (spelling error)
- Update configuration.md (#553) [Bruno Rocha, Konstantin]

  Change spelling error
- HOTFIX: Add coverage for 2 lines on validators. [Bruno Rocha]
- Add the ability for selective validation (#549) [Bruno Rocha, Jacob
  Callahan]

  This change introduces the ability to control which sections of a
  settings object are subject to validation.
  This is controlled primarily by two mechanisms.
  1: When creating a settings object, new arguments `validate_only`
     and `validate_exclude` have been added which receive a list of settings
     paths.
  2: When manually calling validate, new arguments `only` and `exclude`
     have been added.
  All of these allow for either a string or list of strings representing
  settings paths. For example:
      `settings.validators.validate(only=["settings.something",
      "settings.another"])`

      settings = Dynaconf(..., validate_exclude="settings.bad")

  Fixes #508
- Bump mkdocs-material from 7.0.5 to 7.0.6 (#552) [dependabot-
  preview[bot]]

  Bumps [mkdocs-material](https://github.com/squidfunk/mkdocs-material) from 7.0.5 to 7.0.6.
  - [Release notes](https://github.com/squidfunk/mkdocs-material/releases)
  - [Changelog](https://github.com/squidfunk/mkdocs-material/blob/master/docs/changelog.md)
  - [Commits](https://github.com/squidfunk/mkdocs-material/compare/7.0.5...7.0.6)
- Removed release_notes from the docs. (#550) [Bruno Rocha]

  * removed release_notes from the docs.

  towncrier will be implemented soon

  * fix #551
- Demo link (#546) [Bruno Rocha]

  * Add demo link, add better docstring.

  > **DEMO:** You can see a working demo here: https://github.com/rochacbruno/learndynaconf

  * add reference to Rust hydroconf
- Release version 3.1.4. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (3):
            Release version 3.1.3
            HOTFIX for 501 (#540)
            HOTFIX for 462 related issue, `default` on .get should be parsed as Box (#541)

      dependabot-preview[bot] (2):
            Bump mkdocs-material from 6.1.6 to 7.0.4 (#537)
            Bump mkdocs-material from 7.0.4 to 7.0.5 (#539)


3.1.5 (2021-08-20)
------------------
- Release version 3.1.5. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (4):
            Fix #595 namedtuples are no more converted to BoxList (#623)
            fix #596 django override (#645)
            fix #491 pytest django Fix #491 pytest and django (#646)
            Delete requirements.txt

      FrankBattaglia (1):
            fix dict iterator methods for flask DynaconfConfig (#581)

      Robert Rosca (1):
            Add a warning if `--env` is passed to `init` (#629)

      Tanya Tereshchenko (1):
            Do not search anywhere if the absolute path to a file provided (#570)
- Delete requirements.txt. [Bruno Rocha]
- Fix #491 pytest django Fix #491 pytest and django (#646) [Bruno Rocha]
- Fix #596 django override (#645) [Bruno Rocha]

  * Fix #596 django.test.override issue

  * Fix CI side effects
- Add a warning if `--env` is passed to `init` (#629) [Bruno Rocha,
  Bruno Rocha, Robert Rosca]

  * Add a warning if `--env` is passed to `init`

  * Fix typo, `file` was doubled in init help

  * Update docstrings for CLI

  * Raise error if using `-i` with `init` subcommand

  * Update docs to match current behaviour

  * add test coverage
- Fix dict iterator methods for flask DynaconfConfig (#581) [Bruno
  Rocha, Frank Battaglia, FrankBattaglia]
- Fix #595 namedtuples are no more converted to BoxList (#623) [Bruno
  Rocha]
- Do not search anywhere if the absolute path to a file provided (#570)
  [Bruno Rocha, Tanya Tereshchenko]

  * Do not search anywhere if the absolute path to a file provided

  fixes #569

  * Fix test coverage and added some comments.


3.1.4 (2021-03-08)
------------------
- Release version 3.1.4. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (3):
            Release version 3.1.3
            HOTFIX for 501 (#540)
            HOTFIX for 462 related issue, `default` on .get should be parsed as Box (#541)

      dependabot-preview[bot] (2):
            Bump mkdocs-material from 6.1.6 to 7.0.4 (#537)
            Bump mkdocs-material from 7.0.4 to 7.0.5 (#539)
- HOTFIX for 462 related issue, `default` on .get should be parsed as
  Box (#541) [Bruno Rocha]

  objects

  In order to keep the same method api, default values should be parsed
  and converted to Boxed objects.

  https://github.com/rochacbruno/dynaconf/issues/462
- HOTFIX for 501 (#540) [Bruno Rocha]

  Flask still missing __contains__
- Bump mkdocs-material from 7.0.4 to 7.0.5 (#539) [dependabot-
  preview[bot]]

  Bumps [mkdocs-material](https://github.com/squidfunk/mkdocs-material) from 7.0.4 to 7.0.5.
  - [Release notes](https://github.com/squidfunk/mkdocs-material/releases)
  - [Changelog](https://github.com/squidfunk/mkdocs-material/blob/master/docs/changelog.md)
  - [Commits](https://github.com/squidfunk/mkdocs-material/compare/7.0.4...7.0.5)
- Bump mkdocs-material from 6.1.6 to 7.0.4 (#537) [dependabot-
  preview[bot]]

  Bumps [mkdocs-material](https://github.com/squidfunk/mkdocs-material) from 6.1.6 to 7.0.4.
  - [Release notes](https://github.com/squidfunk/mkdocs-material/releases)
  - [Changelog](https://github.com/squidfunk/mkdocs-material/blob/master/docs/changelog.md)
  - [Commits](https://github.com/squidfunk/mkdocs-material/compare/6.1.6...7.0.4)
- Release version 3.1.3. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (4):
            Release version 3.1.3rc1
            Fix #462 make DynaBox nested List to use DynaBox as default class (#533)
            Fix #478 Make alias for environment -> environments (#534)
            Test to ensure #467 is not an issue (#535)


3.1.3 (2021-03-04)
------------------

Fix
~~~
- Environment variables filtering #470 (#474) [Michal Odnous]

Other
~~~~~
- Release version 3.1.3. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (4):
            Release version 3.1.3rc1
            Fix #462 make DynaBox nested List to use DynaBox as default class (#533)
            Fix #478 Make alias for environment -> environments (#534)
            Test to ensure #467 is not an issue (#535)
- Test to ensure #467 is not an issue (#535) [Bruno Rocha]

  Closes #467
- Fix #478 Make alias for environment -> environments (#534) [Bruno
  Rocha]

  This is a commom mistake to pass `environment` so it is alias.

  Fix #478
- Fix #462 make DynaBox nested List to use DynaBox as default class
  (#533) [Bruno Rocha]

  Fix #462
- Release version 3.1.3rc1. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (11):
            Release version 3.1.2
            Fix #445 casting on dottet get. (#446)
            Fix docs regarding --django argument on cli (#477)
            Fix #521 - FlaskDynaconf should raise KeyError for non existing keys (#522)
            Case insensitive envvar traversal (#524)
            Allow load_file to accept pathlib.Path (#525)
            Allow Title case lookup and validation. (#526)
            Fix #482 - formatter case insensitive (#527)
            Fix #449 - Django lazy templating Fix #449 (#528)
            Added a test to reproduce #492 (not able to reproduce) (#530)
            Fix #511 allow user to specify loaders argument to execute_loaders (#531)

      FrankBattaglia (1):
            Specify flask extension initializers by entry point object reference (#456)

      Ilito Torquato (3):
            fix merging hyperlink to fix  #454 (#458)
            Changed enabled_core_loaders elements to be upper case to fix #455 (#457)
            Fix doc secrets from vault #403 (#459)

      Marcelo Lino (1):
            Add __contains__ to Dynaconf (#502)

      Michal Odnous (1):
            Fix: Environment variables filtering #470 (#474)

      dependabot-preview[bot] (5):
            Bump mkdocs-material from 6.0.2 to 6.1.0 (#453)
            Bump mkdocs-git-revision-date-localized-plugin from 0.5.2 to 0.7.3 (#463)
            Bump mkdocs-material from 6.1.0 to 6.1.5 (#473)
            Bump mkdocs-versioning from 0.2.1 to 0.3.1 (#475)
            Bump mkdocs-material from 6.1.5 to 6.1.6 (#476)

      mirrorrim (1):
            Fix reading secret from Vault kv v2 (#483) (#487)
- Fix #511 allow user to specify loaders argument to execute_loaders
  (#531) [Bruno Rocha]

  Fix #511

  ```py
  settings.execute_loaders(loaders=[dynaconf.loaders.env_loader])
  ```
- Added a test to reproduce #492 (not able to reproduce) (#530) [Bruno
  Rocha]

  I can't reproduce the bug #492 but I added a test to ensure.
- Fix #449 - Django lazy templating Fix #449 (#528) [Bruno Rocha]

  * Fix django laxy templates fix #449

  * Delete unused files

  * Fix LOADERS enabling
- Fix #482 - formatter case insensitive (#527) [Bruno Rocha]

  * Fix #482 - formatter using both upper and lowercase access

  Fix #482

  * add more testes covering nested formatting
- Allow Title case lookup and validation. (#526) [Bruno Rocha]

  Fix #486
- Allow load_file to accept pathlib.Path (#525) [Bruno Rocha]

  * Allow load_file to accept pathlib.Path

  Fix #494

  * python 3.6 can't handle Pathlib base path addition to os.path
- Case insensitive envvar traversal (#524) [Bruno Rocha]

  * Envvar traversal is now case insensitive - Fix #519 and fix #516

  Fix #519
  Fix #516

  Now `export DYNACONF_FOO__bar__zaz` is the same as
  `DYNACONF_FOO__BAR__ZAZ`

  > first level prefix still needs to be uppercase!

  Added a warning about django to the docs.

  * Add functional test for issue #519
- Fix #521 - FlaskDynaconf should raise KeyError for non existing keys
  (#522) [Bruno Rocha]

  * Fix #521 - FlaskDynaconf should raise KeyError for non existing keys

  * Test coverage got dotted get
- Add __contains__ to Dynaconf (#502) [Marcelo Lino, Marcelo Lino]

  * Add __contains__ to Dynaconf

  * Add contains assert for flask test

  * Remove duplicated contains from dynaconf
- Fix reading secret from Vault kv v2 (#483) (#487) [Alexey Tylindus,
  mirrorrim]
- Fix docs regarding --django argument on cli (#477) [Bruno Rocha]

  fix #465
  fix #451
- Bump mkdocs-material from 6.1.5 to 6.1.6 (#476) [dependabot-
  preview[bot]]

  Bumps [mkdocs-material](https://github.com/squidfunk/mkdocs-material) from 6.1.5 to 6.1.6.
  - [Release notes](https://github.com/squidfunk/mkdocs-material/releases)
  - [Changelog](https://github.com/squidfunk/mkdocs-material/blob/master/docs/changelog.md)
  - [Commits](https://github.com/squidfunk/mkdocs-material/compare/6.1.5...6.1.6)
- Bump mkdocs-versioning from 0.2.1 to 0.3.1 (#475) [dependabot-
  preview[bot]]

  Bumps [mkdocs-versioning](https://github.com/zayd62/mkdocs-versioning) from 0.2.1 to 0.3.1.
  - [Release notes](https://github.com/zayd62/mkdocs-versioning/releases)
  - [Commits](https://github.com/zayd62/mkdocs-versioning/compare/0.2.1...0.3.1)
- Bump mkdocs-material from 6.1.0 to 6.1.5 (#473) [dependabot-
  preview[bot]]

  Bumps [mkdocs-material](https://github.com/squidfunk/mkdocs-material) from 6.1.0 to 6.1.5.
  - [Release notes](https://github.com/squidfunk/mkdocs-material/releases)
  - [Changelog](https://github.com/squidfunk/mkdocs-material/blob/master/docs/changelog.md)
  - [Commits](https://github.com/squidfunk/mkdocs-material/compare/6.1.0...6.1.5)
- Bump mkdocs-git-revision-date-localized-plugin from 0.5.2 to 0.7.3
  (#463) [dependabot-preview[bot]]

  Bumps [mkdocs-git-revision-date-localized-plugin](https://github.com/timvink/mkdocs-git-revision-date-localized-plugin) from 0.5.2 to 0.7.3.
  - [Release notes](https://github.com/timvink/mkdocs-git-revision-date-localized-plugin/releases)
  - [Commits](https://github.com/timvink/mkdocs-git-revision-date-localized-plugin/compare/v0.5.2...v0.7.3)
- Fix doc secrets from vault #403 (#459) [Bruno Rocha, Ilito Torquato,
  Ilito Torquato]

  * Fix secrets`s doc at Using Vault Server session

  * Fix secrets`s doc at Using Vault Server session

  * Revert "Fix secrets`s doc at Using Vault Server session"

  This reverts commit c47cd986bf089b3528e5c0e7c5a914cb7c1e69c8.
- Changed enabled_core_loaders elements to be upper case to fix #455
  (#457) [Bruno Rocha, Ilito Torquato, Ilito Torquato]

  * Changed enabled_core_loaders elements to be upper case to fix #455

  * Change map to list comprehension and create empty [] as default value

  * fix wrong identation
- Fix merging hyperlink to fix  #454 (#458) [Ilito Torquato, Ilito
  Torquato]
- Specify flask extension initializers by entry point object reference
  (#456) [FrankBattaglia]
- Bump mkdocs-material from 6.0.2 to 6.1.0 (#453) [dependabot-
  preview[bot]]

  Bumps [mkdocs-material](https://github.com/squidfunk/mkdocs-material) from 6.0.2 to 6.1.0.
  - [Release notes](https://github.com/squidfunk/mkdocs-material/releases)
  - [Changelog](https://github.com/squidfunk/mkdocs-material/blob/master/docs/changelog.md)
  - [Commits](https://github.com/squidfunk/mkdocs-material/compare/6.0.2...6.1.0)
- Fix #445 casting on dottet get. (#446) [Bruno Rocha]

  * Fix #445 casting on dottet get.

  Fix the rebound of `cast` on dotted get.

  Fix #445

  * better handling of casting data
- Release version 3.1.2. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (13):
            Release version 3.1.1
            Update diagram images
            Update docs/release_notes
            Fixing prospector warnings. (#425)
            Fix mkdocs config problem found in #423
            Signed in for https://xscode.com/rochacbruno/dynaconf (#426)
            Remove links to outdated issues from guidelines
            Fix colors and KEyError handling on cli.py (#429)
            Fix #434 setenv failing to unset LazyValues (#437)
            Fix #432 no need for warning when env is missing on a file (#438)
            Add test to ensure fix #430 (#439)
            Close #284 not a bug (#440)
            Fix #443 object merge with same value on same level keys (#444)

      dependabot-preview[bot] (6):
            Bump mkdocs-material from 5.3.2 to 5.5.13 (#423)
            Bump pymdown-extensions from 7.1 to 8.0 (#422)
            Bump mkdocs-material-extensions from 1.0 to 1.0.1 (#427)
            Bump pymdown-extensions from 8.0 to 8.0.1 (#435)
            Bump mkdocs-material from 5.5.13 to 6.0.1 (#436)
            Bump mkdocs-material from 6.0.1 to 6.0.2 (#442)


3.1.2 (2020-10-08)
------------------
- Release version 3.1.2. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (13):
            Release version 3.1.1
            Update diagram images
            Update docs/release_notes
            Fixing prospector warnings. (#425)
            Fix mkdocs config problem found in #423
            Signed in for https://xscode.com/rochacbruno/dynaconf (#426)
            Remove links to outdated issues from guidelines
            Fix colors and KEyError handling on cli.py (#429)
            Fix #434 setenv failing to unset LazyValues (#437)
            Fix #432 no need for warning when env is missing on a file (#438)
            Add test to ensure fix #430 (#439)
            Close #284 not a bug (#440)
            Fix #443 object merge with same value on same level keys (#444)

      dependabot-preview[bot] (6):
            Bump mkdocs-material from 5.3.2 to 5.5.13 (#423)
            Bump pymdown-extensions from 7.1 to 8.0 (#422)
            Bump mkdocs-material-extensions from 1.0 to 1.0.1 (#427)
            Bump pymdown-extensions from 8.0 to 8.0.1 (#435)
            Bump mkdocs-material from 5.5.13 to 6.0.1 (#436)
            Bump mkdocs-material from 6.0.1 to 6.0.2 (#442)
- Fix #443 object merge with same value on same level keys (#444) [Bruno
  Rocha]

  This solution is a temporary solution as it solves current
  problem, but there is still the case for `None` values.

  The best solution for this case would be wrapping all the values
  on assignment and give it a full path signature to compare.
- Bump mkdocs-material from 6.0.1 to 6.0.2 (#442) [dependabot-
  preview[bot]]

  Bumps [mkdocs-material](https://github.com/squidfunk/mkdocs-material) from 6.0.1 to 6.0.2.
  - [Release notes](https://github.com/squidfunk/mkdocs-material/releases)
  - [Changelog](https://github.com/squidfunk/mkdocs-material/blob/master/docs/changelog.md)
  - [Commits](https://github.com/squidfunk/mkdocs-material/compare/6.0.1...6.0.2)
- Close #284 not a bug (#440) [Bruno Rocha]

  284 is not a bug but a missing of explicit merge tokens
- Add test to ensure fix #430 (#439) [Bruno Rocha]

  I could not reproduce the problem resported on #430
  considering it close #430
  reopen as needed.
- Fix #432 no need for warning when env is missing on a file (#438)
  [Bruno Rocha]

  When env is missing on a file ther eis no need to output
  a warning.

  All envs are optional on files.

  Fix #432
- Fix #434 setenv failing to unset LazyValues (#437) [Bruno Rocha]

  Fix #434
- Bump mkdocs-material from 5.5.13 to 6.0.1 (#436) [dependabot-
  preview[bot]]

  Bumps [mkdocs-material](https://github.com/squidfunk/mkdocs-material) from 5.5.13 to 6.0.1.
  - [Release notes](https://github.com/squidfunk/mkdocs-material/releases)
  - [Changelog](https://github.com/squidfunk/mkdocs-material/blob/master/docs/changelog.md)
  - [Commits](https://github.com/squidfunk/mkdocs-material/compare/5.5.13...6.0.1)
- Bump pymdown-extensions from 8.0 to 8.0.1 (#435) [dependabot-
  preview[bot]]

  Bumps [pymdown-extensions](https://github.com/facelessuser/pymdown-extensions) from 8.0 to 8.0.1.
  - [Release notes](https://github.com/facelessuser/pymdown-extensions/releases)
  - [Commits](https://github.com/facelessuser/pymdown-extensions/compare/8.0...8.0.1)
- Fix colors and KEyError handling on cli.py (#429) [Bruno Rocha]
- Remove links to outdated issues from guidelines. [Bruno Rocha]
- Bump mkdocs-material-extensions from 1.0 to 1.0.1 (#427) [dependabot-
  preview[bot]]

  Bumps [mkdocs-material-extensions](https://github.com/facelessuser/mkdocs-material-extensions) from 1.0 to 1.0.1.
  - [Release notes](https://github.com/facelessuser/mkdocs-material-extensions/releases)
  - [Changelog](https://github.com/facelessuser/mkdocs-material-extensions/blob/master/changelog.md)
  - [Commits](https://github.com/facelessuser/mkdocs-material-extensions/compare/1.0...1.0.1)
- Signed in for https://xscode.com/rochacbruno/dynaconf (#426) [Bruno
  Rocha]

  Offering paid support for dynaconf users.
- Bump pymdown-extensions from 7.1 to 8.0 (#422) [dependabot-
  preview[bot]]

  Bumps [pymdown-extensions](https://github.com/facelessuser/pymdown-extensions) from 7.1 to 8.0.
  - [Release notes](https://github.com/facelessuser/pymdown-extensions/releases)
  - [Commits](https://github.com/facelessuser/pymdown-extensions/compare/7.1...8.0)
- Bump mkdocs-material from 5.3.2 to 5.5.13 (#423) [dependabot-
  preview[bot]]

  Bumps [mkdocs-material](https://github.com/squidfunk/mkdocs-material) from 5.3.2 to 5.5.13.
  - [Release notes](https://github.com/squidfunk/mkdocs-material/releases)
  - [Changelog](https://github.com/squidfunk/mkdocs-material/blob/master/docs/changelog.md)
  - [Commits](https://github.com/squidfunk/mkdocs-material/compare/5.3.2...5.5.13)
- Fix mkdocs config problem found in #423. [Bruno Rocha]

  Fix #mkdocs-material/1941
- Fixing prospector warnings. (#425) [Bruno Rocha]

  * Fixing prospector warnings

  * Used vulture to detect and remove dead code
- Update docs/release_notes. [Bruno Rocha]
- Update diagram images. [Bruno Rocha]
- Release version 3.1.1. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (2):
            Release version 3.1.1rc6
            HOTFIX: Cli now accepts dotter keys


3.1.1 (2020-09-21)
------------------
- Release version 3.1.1. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (2):
            Release version 3.1.1rc6
            HOTFIX: Cli now accepts dotter keys
- HOTFIX: Cli now accepts dotter keys. [Bruno Rocha]
- Release version 3.1.1rc6. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (2):
            Release version 3.1.1rc5
            Do not include vendor_src on wheel target (#420)
- Do not include vendor_src on wheel target (#420) [Bruno Rocha]
- Release version 3.1.1rc5. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (3):
            Release version 3.1.1rc4
            Small fix on release script
            Minification of vendored modules (#419)
- Minification of vendored modules (#419) [Bruno Rocha]

  * Minified all the vendor folder saving 50% od disk space

  * Add vendor_src and minify script

  vendor_src is not included in the build, only the results of its
  minification
- Small fix on release script. [Bruno Rocha]

  Correct path for mkdocs.yml
- Release version 3.1.1rc4. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (3):
            Release version 3.1.1rc3
            HOTFIX: Add missing instruction to release.sh
            Added full Dynaconf Diagram and few fizes. (#418)
- Added full Dynaconf Diagram and few fizes. (#418) [Bruno Rocha]
- HOTFIX: Add missing instruction to release.sh. [Bruno Rocha]
- Release version 3.1.1rc3. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (5):
            Release version 3.1.1rc2
            Fix set attribute directly and fresh vars (#412)
            384 fix tail and dotted merge (#415)
            Fix #404 no more dup message on combined validators (#417)
            HOTFIX 414 update docs version on release

      Max Winterstein (1):
            Fix typo in release notes (#411)

      Mirek Długosz (1):
            Fix #407 - add proper equality test for CombinedValidator (#413)
- HOTFIX 414 update docs version on release. [Bruno Rocha]

  Fix #414
- Fix #404 no more dup message on combined validators (#417) [Bruno
  Rocha]
- 384 fix tail and dotted merge (#415) [Bruno Rocha]

  * attempt to fix tail call on object_merge Fix #384

  * Fix list and dict merge issues
- Fix typo in release notes (#411) [Bruno Rocha, Max Winterstein]
- Fix #407 - add proper equality test for CombinedValidator (#413)
  [Mirek Długosz]

  * Fix #407 - add proper equality test for CombinedValidator

  * Update after review
- Fix set attribute directly and fresh vars (#412) [Bruno Rocha]

  * Fix set attribute directly and fresh vars

  Fix #253
  Fix #395

  * No need to check for default_settings in setattr
- Release version 3.1.1rc2. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (2):
            Release version 3.1.1rc1
            HOTFIX: Logging instance has a `formatter` attribute (#410)
- HOTFIX: Logging instance has a `formatter` attribute (#410) [Bruno
  Rocha]

  Dynaconf was trying to detect a lazy value by the existence
  of `formatter` attribute but in Django when the value is a logging
  it has `.formatter` attribute.
- Release version 3.1.1rc1. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (10):
            Release version 3.1.0
            Create FUNDING.yml
            Fix #391 make box_settings optional, change vendoring strategy (#398)
            HOTFIX: Add missing vendor.txt
            Allow nested Lazy Values (#405)
            Makes   PEP8 more strictly and remove unused variables (#408)
            Merge branch 'master' into vault
            boto is optional
            Merge branch 'vault' into master
            Included example of custom SOPS loader to the docs

      Christoph Schmatzler (1):
            Fix typo in Validation docs (#394)

      Gabriel Simonetto (1):
            Fix #399 - Update documentation link (#401)

      Jiranun Jiratrakanvong (1):
            Add auth username and password for redis settings (#378)

      Martijn Pieters (1):
            Correct typos in documentation and README (#400)

      Mirek Długosz (1):
            Test all names in Validator("foo", "bar", must_exist=False) (#406)

      Nikolai Bessonov (1):
            fix a typo (#393)

      Peng Yin (5):
            Read all secrets under a vault path
            Add option to auth vault with iam role
            Fix format
            Fix test for versioned kv engine in latest vault
            Merge branch 'master' into vault

      whg517 (1):
            docs: Fixed filename error in the case of the index page (#396)
- Included example of custom SOPS loader to the docs. [Bruno Rocha]
- Add auth username and password for redis settings (#378) [Bruno Rocha,
  Jiranun Jiratrakanvong, Jiranun Jiratrakanvong]
- Merge branch 'vault' into master. [Bruno Rocha]
- Boto is optional. [Bruno Rocha]
- Merge branch 'master' into vault. [Bruno Rocha]
- Fix a typo (#393) [Bruno Rocha, Nikolai Bessonov]
- Fix typo in Validation docs (#394) [Bruno Rocha, Christoph Schmatzler]
- Correct typos in documentation and README (#400) [Bruno Rocha, Martijn
  Pieters]

  * Correct minor documentation typo in the Dynamic Variables section.

  * Fix typos throughout the docs
- Docs: Fixed filename error in the case of the index page (#396) [Bruno
  Rocha, whg517]
- Fix #399 - Update documentation link (#401) [Bruno Rocha, Gabriel
  Simonetto]
- Makes   PEP8 more strictly and remove unused variables (#408) [Bruno
  Rocha]
- Test all names in Validator("foo", "bar", must_exist=False) (#406)
  [Mirek Długosz]

  `Validator(must_exist=False)` incorrectly checked first name only.
  Given settings.yaml:

     bar: some_value

  `Validator("foo", "bar", must_exist=False)` would **not** raise
  ValidationError - it would return after checking that first name
  indeed is not defined.
- Allow nested Lazy Values (#405) [Bruno Rocha]

  Fix #392
  Fix #402
- Merge branch 'master' into vault. [Peng Yin]
- HOTFIX: Add missing vendor.txt. [Bruno Rocha]
- Fix #391 make box_settings optional, change vendoring strategy (#398)
  [Bruno Rocha]

  - Revert DynaBox box_settings to be optional
  - Change vendoring strategy
     - instead of hacking sys.modules, using abs paths
  - Pin to Box 4.2.2 without conflicting with system installed box
  - Added a Django example on tests to fix @daviddavis reported issue
- Fix test for versioned kv engine in latest vault. [Peng Yin]
- Fix format. [Peng Yin]
- Add option to auth vault with iam role. [Peng Yin]
- Read all secrets under a vault path. [Peng Yin]
- Create FUNDING.yml. [Bruno Rocha]
- Release version 3.1.0. [Bruno Rocha]

  Shortlog of commits since last release:

      Andreas Poehlmann (1):
            Allow importing SEARCHTREE before settings are configured (#383)

      Bruno Rocha (10):
            Release version 3.0.0
            Hot fix removing unused imports
            Merge branch 'master' of github.com:rochacbruno/dynaconf
            Removing invalid links, adding allert on old docs  fix #369 and fix #371 (#372)
            Fix #359 lazy template substitution on nested keys (#375)
            Flask fizes and other issues included. (#376)
            Fix #379 dict like iteration (#385)
            Fix #377 allow computed values (#386)
            Fix #388 URL reference for custom loaders (#389)
            Fix #382 add is_overriden method (#390)

      John Vandenberg (1):
            Allow testing against local redis server (#387)

      Piotr Baniukiewicz (1):
            Fix validation of optional fields (#370)


3.1.0 (2020-08-14)
------------------
- Release version 3.1.0. [Bruno Rocha]

  Shortlog of commits since last release:

      Andreas Poehlmann (1):
            Allow importing SEARCHTREE before settings are configured (#383)

      Bruno Rocha (10):
            Release version 3.0.0
            Hot fix removing unused imports
            Merge branch 'master' of github.com:rochacbruno/dynaconf
            Removing invalid links, adding allert on old docs  fix #369 and fix #371 (#372)
            Fix #359 lazy template substitution on nested keys (#375)
            Flask fizes and other issues included. (#376)
            Fix #379 dict like iteration (#385)
            Fix #377 allow computed values (#386)
            Fix #388 URL reference for custom loaders (#389)
            Fix #382 add is_overriden method (#390)

      John Vandenberg (1):
            Allow testing against local redis server (#387)

      Piotr Baniukiewicz (1):
            Fix validation of optional fields (#370)
- Allow importing SEARCHTREE before settings are configured (#383)
  [Andreas Poehlmann]
- Allow testing against local redis server (#387) [John Vandenberg]
- Fix #382 add is_overriden method (#390) [Bruno Rocha]

  Fix #382 add is_overriden method for DJDT
- Fix #388 URL reference for custom loaders (#389) [Bruno Rocha]

  Fix #388 URL reference for custom loaders
- Fix #377 allow computed values (#386) [Bruno Rocha]

  This fixes #377 by allowing Validator to provide default values.
- Fix #379 dict like iteration (#385) [Bruno Rocha]

  * Fix #379 add missing __iter__ and items

  * Fix docs
- Flask fizes and other issues included. (#376) [Bruno Rocha]

  Fix #323
  Fix #325
  Fix #327
  Fix #341

  Exemples added:

  	example/issues/323_DEFAULT_VALUES_RESOLUTION/
  	example/issues/325_flask_dot_env/
  	example/issues/327_flask_extensions_warning/
  	example/issues/341_box_it_up/
- Fix #359 lazy template substitution on nested keys (#375) [Bruno
  Rocha]
- Removing invalid links, adding allert on old docs  fix #369 and fix
  #371 (#372) [Bruno Rocha]
- Merge branch 'master' of github.com:rochacbruno/dynaconf. [Bruno
  Rocha]
- Fix validation of optional fields (#370) [Bruno Rocha
  <rochacbruno@users.noreply.github.com>    Co-authored-by: Bruno Rocha
  <rochacbruno@users.noreply.github.com>, Piotr Baniukiewicz]

  * Fix validation of optional fields

  * More concise code
- Hot fix removing unused imports. [Bruno Rocha]
- Release version 3.0.0. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (5):
            Release version 3.0.0rc2
            Improvements on CLI and init command (#363)
            Writing new docs page 1 (#364)
            Add netlify (#366)
            Add netlify runtime file...


3.0.0 (2020-06-29)
------------------
- Release version 3.0.0. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (5):
            Release version 3.0.0rc2
            Improvements on CLI and init command (#363)
            Writing new docs page 1 (#364)
            Add netlify (#366)
            Add netlify runtime file...
- Add netlify runtime file... [Bruno Rocha]
- Add netlify (#366) [Bruno Rocha]
- Writing new docs page 1 (#364) [Bruno Rocha]

  * porting docs to mkdocs

  * Docs First Page

  * New docs ok
- Improvements on CLI and init command (#363) [Bruno Rocha]
- Release version 3.0.0rc2. [Bruno Rocha]

  Shortlog of commits since last release:

      Bernardo Gomes (2):
            Adding f string (#319)
            Added little information about how dev into this project. (#321)

      Bruno Rocha (18):
            Release version 3.0.0rc1
            Better exception handling on env_loader (#316)
            Add support for config aliases (#332)
            Add ENVLESS_MODE (#337)
            Fix #272 allow access of lowercase keys (#338)
            Fix #298 allow auto complete for editors and console (#339)
            Vendoring dependencies Fix #301 (#345)
            Clean tox installation for local testing (#346)
            Validator improvements on conditions (#353)
            Add note about quoting in env vars (#347)
            DEPRECATED global settings object.
            DEPRECATED global settings object. (#356)
            Lowecase read allowed by default (#357)
            Merge branch 'master' of github.com:rochacbruno/dynaconf
            envless by default - breaking change ⚠️ (#358)
            dotenv is no more loaded by default (#360)
            No more loading of `settings.*` by default (#361)
            NO more logger and debug messages (#362)

      Douglas Maciel d'Auriol Souza (1):
            Insert news validator conditions: (len_eq, len_ne, len_min, len_max, contd) (#328)

      Jeff Wayne (1):
            s/DYNACONF_ENV/ENV_FOR_DYNACONF (#335)

      Marcos Benevides (1):
            Fix minor typo in Flask extension docs (#318)

      Nicholas Nadeau, Ph.D., P.Eng (1):
            Fixed comma typo (#334)

      sfunkhouser (1):
            Add option to override default mount_point for vault (#349)
- NO more logger and debug messages (#362) [Bruno Rocha]

  * logger and DEBUG_LEVEL has gone.

  * Add logger as a backwards compat method
- No more loading of `settings.*` by default (#361) [Bruno Rocha]
- Dotenv is no more loaded by default (#360) [Bruno Rocha]
- Envless by default - breaking change ⚠️ (#358) [Bruno Rocha]

  * ⚠️ Turning the default to be the envless mode (this is breaking change) ⚠️

  ⚠️ THIS IS BREAKING CHANGE ⚠️

  * envless by default is done

  * Fix redis and vault tests

  * CLI default to global instance with warnings
- Merge branch 'master' of github.com:rochacbruno/dynaconf. [Bruno
  Rocha]
- Lowecase read allowed by default (#357) [Bruno Rocha]

  * DEPRECATED global settings object.

  No more `from dynaconf import settings`

  * Lower case first level keys are now allowed by default
- DEPRECATED global settings object. (#356) [Bruno Rocha]

  No more `from dynaconf import settings`
- DEPRECATED global settings object. [Bruno Rocha]

  No more `from dynaconf import settings`
- Add note about quoting in env vars (#347) [Bruno Rocha]
- Validator improvements on conditions (#353) [Bruno Rocha]

  * Validators improvements

  * add cast argument to validators
- Add option to override default mount_point for vault (#349)
  [sfunkhouser]
- Clean tox installation for local testing (#346) [Bruno Rocha]
- Vendoring dependencies Fix #301 (#345) [Bruno Rocha]
- Fix #298 allow auto complete for editors and console (#339) [Bruno
  Rocha]

  implemented `__dir__` on Settings and Dynabox
- Fix #272 allow access of lowercase keys (#338) [Bruno Rocha]

  - `settings.lowercase_key` is allowed
  - `settings.dynaconf` is a proxy to internal methods
  - `settings.__reserved_attributes` validates key names
  - `LazySettings __init__ parameters can receive lower case configs`
- Add ENVLESS_MODE (#337) [Bruno Rocha]
- S/DYNACONF_ENV/ENV_FOR_DYNACONF (#335) [Jeff Wayne]
- Fixed comma typo (#334) [Nicholas Nadeau, Ph.D., P.Eng]
- Add support for config aliases (#332) [Bruno Rocha]

  All _FOR_DYNACONF can now be aliased when passing to LazySettings.
- Insert news validator conditions: (len_eq, len_ne, len_min, len_max,
  contd) (#328) [Bruno Rocha, Douglas Maciel d'Auriol Souza]

  * Insert news validator conditions: len_eq, len_ne, len_min, len_max, contd

  * Insert news validator conditions: len_eq, len_ne, len_min, len_max, contd

  * Update validator_conditions.py

  * Update test_validators_conditions.py

  * Checked: Flake8

  * Black sugest

  * Change of the term contd to cont, in order to avoid false interpretation.
- Better exception handling on env_loader (#316) [Bruno Rocha]
- Added little information about how dev into this project. (#321)
  [Bernardo Gomes]
- Adding f string (#319) [Bernardo Gomes]

  * First test to change to f-string

  * second change to f-string

  * Removed 95% of .format(

  * Removed % from code.

  * forget format.

  * Fixing flaked reports.

  * Fixing flaked reports-v2.

  * make run-pre-commit command executed.

  * Little bugfix f of f-string inside of the string.
- Fix minor typo in Flask extension docs (#318) [Marcos Benevides]
- Release version 3.0.0rc1. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (8):
            Release version 2.2.3
            Changed text format and fixed tests
            Merge branch '304-ShowDataTypeListCli'
            Fix issue #305 - printing and exporting LazyFormat (#312)
            Fix #288 - Nullable values (#300)
            Default to ruamel.yaml when it is available. (#313)
            Fix #306 - does not defaults to merge, deprecated reset - [Breaking Change] (#315)
            HOTFIX - tox.ini drops 3.5

      Tiago Cordeiro (1):
            Added OSX builds to the Azure Pipeline (#307)

      Vicente Marçal (1):
            Changed CLI list to show data type of the envvars to fix #304

      dependabot-preview[bot] (1):
            Unpinning python-box, removing box_it_up and default_box arguments (#279)
- HOTFIX - tox.ini drops 3.5. [Bruno Rocha]
- Fix #306 - does not defaults to merge, deprecated reset - [Breaking
  Change] (#315) [Bruno Rocha]

  - Don't default to `merge` for `__` variables
  - Made `@merge` more explicit and smart
  - Deprecated `@reset`
- Unpinning python-box, removing box_it_up and default_box arguments
  (#279) [Bruno Rocha, dependabot-preview[bot]]
- Default to ruamel.yaml when it is available. (#313) [Bruno Rocha]
- Fix #288 - Nullable values (#300) [Bruno Rocha]

  * Attempt to fix #288 (needs more debugging)

  * Fixing bug on DynaBox.get
- Fix issue #305 - printing and exporting LazyFormat (#312) [Bruno
  Rocha]
- Merge branch '304-ShowDataTypeListCli' [Bruno Rocha]
- Changed text format and fixed tests. [Bruno Rocha]
- Changed CLI list to show data type of the envvars to fix #304.
  [Vicente Marçal]
- Added OSX builds to the Azure Pipeline (#307) [Tiago Cordeiro]

  * Added OSX builds to the Azure Pipeline

  * Added OSX builds to the Azure Pipeline

  * skip docker tests on macOS
- Release version 2.2.3. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (7):
            Release version 2.2.2
            Fix #273 add Flask load extensions method.
            add t.me badge fix #262
            Fix #145 allow lazy format using os.environ and settings values.
            Overriding strategy test
            Fix #203 document the usage with pytest (with examples)
            unpin dependencies

      Hildeberto (2):
            Fix pre-commit to run python3 rather than python3.7
            Merge pull request #281 from hilam/fix_pre_commit

      JSP (1):
            fix object_merge issue #285 with  meta value

      dependabot-preview[bot] (2):
            Update python-dotenv requirement from <=0.10.3 to <0.10.6
            Update python-dotenv requirement from <0.10.6 to <0.11.1


2.2.3 (2020-02-28)
------------------
- Release version 2.2.3. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (7):
            Release version 2.2.2
            Fix #273 add Flask load extensions method.
            add t.me badge fix #262
            Fix #145 allow lazy format using os.environ and settings values.
            Overriding strategy test
            Fix #203 document the usage with pytest (with examples)
            unpin dependencies

      Hildeberto (2):
            Fix pre-commit to run python3 rather than python3.7
            Merge pull request #281 from hilam/fix_pre_commit

      JSP (1):
            fix object_merge issue #285 with  meta value

      dependabot-preview[bot] (2):
            Update python-dotenv requirement from <=0.10.3 to <0.10.6
            Update python-dotenv requirement from <0.10.6 to <0.11.1
- Unpin dependencies. [Bruno Rocha]
- Update python-dotenv requirement from <0.10.6 to <0.11.1. [dependabot-
  preview[bot]]

  Updates the requirements on [python-dotenv](https://github.com/theskumar/python-dotenv) to permit the latest version.
  - [Release notes](https://github.com/theskumar/python-dotenv/releases)
  - [Changelog](https://github.com/theskumar/python-dotenv/blob/master/CHANGELOG.md)
  - [Commits](https://github.com/theskumar/python-dotenv/compare/v0.1.1...v0.11.0)
- Fix #203 document the usage with pytest (with examples) [Bruno Rocha]
- Overriding strategy test. [Bruno Rocha]
- Fix #145 allow lazy format using os.environ and settings values.
  [Bruno Rocha]
- Add t.me badge fix #262. [Bruno Rocha]
- Fix #273 add Flask load extensions method. [Bruno Rocha]

  - This commit adds a new method `load_extensions` to
  `FlaskDynaconf` class.
- Update python-dotenv requirement from <=0.10.3 to <0.10.6.
  [dependabot-preview[bot]]

  Updates the requirements on [python-dotenv](https://github.com/theskumar/python-dotenv) to permit the latest version.
  - [Release notes](https://github.com/theskumar/python-dotenv/releases)
  - [Changelog](https://github.com/theskumar/python-dotenv/blob/master/CHANGELOG.md)
  - [Commits](https://github.com/theskumar/python-dotenv/compare/v0.1.1...v0.10.5)
- Fix object_merge issue #285 with  meta value. [JSP]
- Merge pull request #281 from hilam/fix_pre_commit. [Hildeberto]

  Fix pre-commit to run python3 rather than python3.7
- Fix pre-commit to run python3 rather than python3.7. [Hildeberto]
- Release version 2.2.2. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (3):
            Release version 2.2.1
            Fix #258 custom message for validators
            Pin python-box version because of a breaking release

      Hildeberto (1):
            Close #178. Included integration tests redis/vault


2.2.2 (2019-12-26)
------------------
- Release version 2.2.2. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (3):
            Release version 2.2.1
            Fix #258 custom message for validators
            Pin python-box version because of a breaking release

      Hildeberto (1):
            Close #178. Included integration tests redis/vault
- Pin python-box version because of a breaking release. [Bruno Rocha]

  The release of python-box https://github.com/cdgriffith/Box/pull/116
  is a breaking change.

  So pinning this until this project addapts.

  Also pinning other direct deps.
- Fix #258 custom message for validators. [Bruno Rocha]
- Close #178. Included integration tests redis/vault. [Hildeberto]
- Release version 2.2.1. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (4):
            Release version 2.2.0
            Fix #251 recursive call was using mutable memoized data (#254)
            Fix #266 created new variable FORCE_ENV to override ENV_FOR_DYNACONF
            Fix coverage for validators

      David Moreau Simard (1):
            Add ara as a user of dynaconf (#252)

      Emmanuel Nosa Evbuomwan (1):
            Update sensitive_secrets.md

      Hildeberto (1):
            Adjust remote upstream URL

      Jan Willhaus (1):
            Add support for detecting duplicate validators being added (and ignore them) (#256)

      Oliver Lehmann (5):
            fix: env_loader.write: quote_mode for non-string values
            : added line break
            fix str comparison
            changing quote logic
            fix open error @py3.5


2.2.1 (2019-12-06)
------------------

Fix
~~~
- Env_loader.write: quote_mode for non-string values. [Oliver Lehmann]

Other
~~~~~
- Release version 2.2.1. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (4):
            Release version 2.2.0
            Fix #251 recursive call was using mutable memoized data (#254)
            Fix #266 created new variable FORCE_ENV to override ENV_FOR_DYNACONF
            Fix coverage for validators

      David Moreau Simard (1):
            Add ara as a user of dynaconf (#252)

      Emmanuel Nosa Evbuomwan (1):
            Update sensitive_secrets.md

      Hildeberto (1):
            Adjust remote upstream URL

      Jan Willhaus (1):
            Add support for detecting duplicate validators being added (and ignore them) (#256)

      Oliver Lehmann (5):
            fix: env_loader.write: quote_mode for non-string values
            : added line break
            fix str comparison
            changing quote logic
            fix open error @py3.5
- Fix coverage for validators. [Bruno Rocha]
- Fix #266 created new variable FORCE_ENV to override ENV_FOR_DYNACONF.
  [Bruno Rocha]
- Adjust remote upstream URL. [Hildeberto]
- Update sensitive_secrets.md. [Emmanuel Nosa Evbuomwan]

  Updated the file reference from `settings`.toml{json|py|ini|yaml} to the convention used thus far; `secrets`.toml{json|py|ini|yaml}. This can help alleviate the slightest chance of the information becoming misleading or confusing. This can also be ignored if Dynaconf can be set to search for secrets in files other than `secrets.<ext>`
- Fix open error @py3.5. [Oliver Lehmann]
- Changing quote logic. [Oliver Lehmann]
- Fix str comparison. [Oliver Lehmann]
- : added line break. [Oliver Lehmann]
- Add support for detecting duplicate validators being added (and ignore
  them) (#256) [Jan Willhaus]
- Fix #251 recursive call was using mutable memoized data (#254) [Bruno
  Rocha]

  replaced with recursive passing of parent data.

  NOTE to SELF: Never! use a mutable memoized data
                Always use `==` to compare when you dont know the types
- Add ara as a user of dynaconf (#252) [David Moreau Simard]
- Release version 2.2.0. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (5):
            Release version 2.1.1
            Fix #236 added .local. files loading and module impersonation docs (#239)
            Replace key.upper with `upperfy` function that keeps `__` attributes (#240)
            Fix #241 new merge standards (#243)
            Add support for PRELOAD_ setting. (#244)

      Kedar Kulkarni (1):
            Fixing how filename.local.* files are loaded (#238)

      paskozdilar (1):
            fix crash on empty settings (#242)


2.2.0 (2019-10-09)
------------------
- Release version 2.2.0. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (5):
            Release version 2.1.1
            Fix #236 added .local. files loading and module impersonation docs (#239)
            Replace key.upper with `upperfy` function that keeps `__` attributes (#240)
            Fix #241 new merge standards (#243)
            Add support for PRELOAD_ setting. (#244)

      Kedar Kulkarni (1):
            Fixing how filename.local.* files are loaded (#238)

      paskozdilar (1):
            fix crash on empty settings (#242)
- Add support for PRELOAD_ setting. (#244) [Bruno Rocha]
- Fix #241 new merge standards (#243) [Bruno Rocha]

  Adds dynaconf_merge and @merge for better merge standards. ref #241
- Fix crash on empty settings (#242) [paskozdilar]

  * fix crash on empty settings

  * add test for empty environment

  * fix PEP 8 issue (expected 2 blank lines, found 1)
- Replace key.upper with `upperfy` function that keeps `__` attributes
  (#240) [Bruno Rocha]
- Fix #236 added .local. files loading and module impersonation docs
  (#239) [Bruno Rocha]

  also MERGE_ENABLED is no more deprecated.
- Fixing how filename.local.* files are loaded (#238) [Kedar Kulkarni]
- Release version 2.1.1. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (7):
            Release version 2.1.0
            Improve validators to use `from_env` method (#225)
            Add info about dunder envvars on django.md docs guide (#226)
            Fix #228 add `ignore` argument to Django explicit mode. (#229)
            Improvement to close #230 - do not throw error for base envs. (#231)
            dynaconf init will not write all possible envs, only [default] (#233)
            When both enabled, Vault has the priority over Redis for overriding (#234)

      Dave Barnow (1):
            Fix typo in CLI init (#227)

      Kedar Kulkarni (1):
            Fixing self._root_path to fall back to os.getcwd() only when `settings.load_file` is called directly or from includes (#232)


2.1.1 (2019-09-16)
------------------
- Release version 2.1.1. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (7):
            Release version 2.1.0
            Improve validators to use `from_env` method (#225)
            Add info about dunder envvars on django.md docs guide (#226)
            Fix #228 add `ignore` argument to Django explicit mode. (#229)
            Improvement to close #230 - do not throw error for base envs. (#231)
            dynaconf init will not write all possible envs, only [default] (#233)
            When both enabled, Vault has the priority over Redis for overriding (#234)

      Dave Barnow (1):
            Fix typo in CLI init (#227)

      Kedar Kulkarni (1):
            Fixing self._root_path to fall back to os.getcwd() only when `settings.load_file` is called directly or from includes (#232)
- When both enabled, Vault has the priority over Redis for overriding
  (#234) [Bruno Rocha]
- Dynaconf init will not write all possible envs, only [default] (#233)
  [Bruno Rocha]
- Fixing self._root_path to fall back to os.getcwd() only when
  `settings.load_file` is called directly or from includes (#232) [Kedar
  Kulkarni]
- Improvement to close #230 - do not throw error for base envs. (#231)
  [Bruno Rocha]
- Fix #228 add `ignore` argument to Django explicit mode. (#229) [Bruno
  Rocha]
- Fix typo in CLI init (#227) [Dave Barnow]
- Add info about dunder envvars on django.md docs guide (#226) [Bruno
  Rocha]
- Improve validators to use `from_env` method (#225) [Bruno Rocha]
- Release version 2.1.0. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (8):
            Release version 2.0.4
            Merge branch 'dgarcia360-master'
            Fix #197 add support for DOTTED__ENV__VARS (#215)
            Add support to export merged env to filesystem via cli. (#217)
            Adds `from_env` method and change `_store` to be a `DynaBox` (#219)
            hotfix: next release will be 2.1.0 because new features added. (#220)
            Fix `make test_examples` to use better assertions, redis and vault loader now respects `envs` (#222)
            fix #221 removed JSON,YAML,INI,TOML cosntants from default_settings (#223)

      Kedar Kulkarni (1):
            Add `list_envs` function to vault loader and now envs can have `_` on its name.

      Pavel Alimpiev (1):
            Fix typo in documentation for a Validator class (#213)

      dgarcia360 (3):
            Updated configuration options table to csv table
            Added responsive table fix
            Fix format


2.1.0 (2019-09-05)
------------------
- Release version 2.1.0. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (8):
            Release version 2.0.4
            Merge branch 'dgarcia360-master'
            Fix #197 add support for DOTTED__ENV__VARS (#215)
            Add support to export merged env to filesystem via cli. (#217)
            Adds `from_env` method and change `_store` to be a `DynaBox` (#219)
            hotfix: next release will be 2.1.0 because new features added. (#220)
            Fix `make test_examples` to use better assertions, redis and vault loader now respects `envs` (#222)
            fix #221 removed JSON,YAML,INI,TOML cosntants from default_settings (#223)

      Kedar Kulkarni (1):
            Add `list_envs` function to vault loader and now envs can have `_` on its name.

      Pavel Alimpiev (1):
            Fix typo in documentation for a Validator class (#213)

      dgarcia360 (3):
            Updated configuration options table to csv table
            Added responsive table fix
            Fix format
- Fix #221 removed JSON,YAML,INI,TOML cosntants from default_settings
  (#223) [Bruno Rocha]

  Default settings should hold only constants ending in _FOR_DYNACONF
- Fix `make test_examples` to use better assertions, redis and vault
  loader now respects `envs` (#222) [Bruno Rocha]
- Hotfix: next release will be 2.1.0 because new features added. (#220)
  [Bruno Rocha]
- Adds `from_env` method and change `_store` to be a `DynaBox` (#219)
  [Bruno Rocha]
- Add `list_envs` function to vault loader and now envs can have `_` on
  its name. [Kedar Kulkarni]

  * Adding new feature to address issue #211 `list_envs ` function on vault loader
  * Removing restriction with env cannot contain underscore chars
- Add support to export merged env to filesystem via cli. (#217) [Bruno
  Rocha]

  fix #200

  ```bash
  dynaconf list -o path/to/file.yaml --output-flat
  ```
- Fix #197 add support for DOTTED__ENV__VARS (#215) [Bruno Rocha]

  * Fix #197 add support for DOTTED__ENV__VARS

  * Full support for `__` - @reset and @del markers
- Merge branch 'dgarcia360-master' [Bruno Rocha]
- Fix format. [dgarcia360]
- Added responsive table fix. [dgarcia360]
- Updated configuration options table to csv table. [dgarcia360]
- Fix typo in documentation for a Validator class (#213) [Pavel
  Alimpiev]
- Release version 2.0.4. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (2):
            Release version 2.0.3
            Fix #207 allow python module path name for includes (#209)

      Michał Bartoszkiewicz (1):
            Update usage.md (#208)

      Pavel Alimpiev (2):
            Refactor Vault integration (#202)
            Update configuration.md (#205)

      Tanveer Alam (2):
            Update usage.md (#196)
            Update usage.md (#195)


2.0.4 (2019-08-22)
------------------
- Release version 2.0.4. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (2):
            Release version 2.0.3
            Fix #207 allow python module path name for includes (#209)

      Michał Bartoszkiewicz (1):
            Update usage.md (#208)

      Pavel Alimpiev (2):
            Refactor Vault integration (#202)
            Update configuration.md (#205)

      Tanveer Alam (2):
            Update usage.md (#196)
            Update usage.md (#195)
- Fix #207 allow python module path name for includes (#209) [Bruno
  Rocha]
- Update usage.md (#208) [Michał Bartoszkiewicz]

  Change 'FLask' to 'Flask'
- Update configuration.md (#205) [Pavel Alimpiev]
- Refactor Vault integration (#202) [Pavel Alimpiev]

  * Add AppRole based authorization for Vault loader

  * Fix default value for VAULT_PATH_FOR_DYNACONF, Update docs

  * HVAC automatically adds /secret/ prefix on read and write access
  * /dynaconf was never added to the VAULT_PATH_FOR_DYNACONF value
  * Docs was inconsistent with the actual code base

  * Fix inconsistency in the docs

  * Remove VAULT_SESSION_FOR_DYNACONF config variable.

  * HVAC's session argument must be a fully initialized Session object,
  that means - it's very complicated to setup Vault client with this
  argument, via default instruments (.toml, .env, etc)
  * Users can still setup this argument by setting up VAULT_FOR_DYNACONF
  directly

  * Update documentation for VAULT_* configuration

  * Fix code style
- Update usage.md (#195) [Tanveer Alam]
- Update usage.md (#196) [Tanveer Alam]
- Release version 2.0.3. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (2):
            Release version 2.0.2
            Fix #194 flask.app.config __setitem__ (#199)

      Jan Willhaus (1):
            Catch BoxKeyError when contents are TOML parsable but not keyable (#192)

      Raoul Snyman (1):
            Use the Key Value API rather than the old 'read' and 'write' methods (#198)


2.0.3 (2019-06-27)
------------------
- Release version 2.0.3. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (2):
            Release version 2.0.2
            Fix #194 flask.app.config __setitem__ (#199)

      Jan Willhaus (1):
            Catch BoxKeyError when contents are TOML parsable but not keyable (#192)

      Raoul Snyman (1):
            Use the Key Value API rather than the old 'read' and 'write' methods (#198)
- Fix #194 flask.app.config __setitem__ (#199) [Bruno Rocha]

  Flask.config was not proxying __setitem__ atribute so this
  change adds a call to __setitem__ on contrib/flask_dynaconf
- Use the Key Value API rather than the old 'read' and 'write' methods
  (#198) [Raoul Snyman]
- Catch BoxKeyError when contents are TOML parsable but not keyable
  (#192) [Jan Willhaus]
- Release version 2.0.2. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (8):
            Release version 2.0.1
            Add note to release script
            Adhering to Github Community Standards (#175)
            removed pytest-xdist (#181)
            Add example and test for issue #182 (#183)
            Fix #179 dynaconf cli shows only user defined vars unless -a used (#188)
            Fix #184 - workdir should walk to root in ipython REPL (#190)
            Fix #189 added `settings.as_dict()` and `dynaconf list -o file.json` (#191)

      Jan Willhaus (4):
            Fix `False` not being an acceptable env (#176)
            Fix  base loader when having no ENVVAR_PREFIX_ (Addresses #177) (#185)
            Hide DeprecationWarning from Pytest when testing for them (#186)
            Replace logging.basicConfig with handler on logger (#187)


2.0.2 (2019-04-29)
------------------
- Release version 2.0.2. [Bruno Rocha]

  Shortlog of commits since last release:

      Bruno Rocha (8):
            Release version 2.0.1
            Add note to release script
            Adhering to Github Community Standards (#175)
            removed pytest-xdist (#181)
            Add example and test for issue #182 (#183)
            Fix #179 dynaconf cli shows only user defined vars unless -a used (#188)
            Fix #184 - workdir should walk to root in ipython REPL (#190)
            Fix #189 added `settings.as_dict()` and `dynaconf list -o file.json` (#191)

      Jan Willhaus (4):
            Fix `False` not being an acceptable env (#176)
            Fix  base loader when having no ENVVAR_PREFIX_ (Addresses #177) (#185)
            Hide DeprecationWarning from Pytest when testing for them (#186)
            Replace logging.basicConfig with handler on logger (#187)
- Fix #189 added `settings.as_dict()` and `dynaconf list -o file.json`
  (#191) [Bruno Rocha]
- Fix #184 - workdir should walk to root in ipython REPL (#190) [Bruno
  Rocha]
- Fix #179 dynaconf cli shows only user defined vars unless -a used
  (#188) [Bruno Rocha]

  Command `dynaconf list` will show only user defined vars
  IF `--all|-a` is passed then it includes internal variables.
- Replace logging.basicConfig with handler on logger (#187) [Jan
  Willhaus]
- Hide DeprecationWarning from Pytest when testing for them (#186) [Jan
  Willhaus]

  * Hide DeprecationWarnings from Pytest when testing for them

  * Use parametrized test instead of repeating code
- Fix  base loader when having no ENVVAR_PREFIX_ (Addresses #177) (#185)
  [Jan Willhaus]

  * Fix `False` not being an acceptable env

  * Additional testcase for prefix being false from envvar

  * Fix mistaken reference to ENVVAR_PREFIX

  * Fix typo
- Add example and test for issue #182 (#183) [Bruno Rocha]

  * Add working example for issue 182

  * Option 2 added

  * Allowed `settings.load_file` programmatically
- Removed pytest-xdist (#181) [Bruno Rocha]

  Now tests run in a separate tmpdir so xdist is not needed anymore
- Fix `False` not being an acceptable env (#176) [Jan Willhaus]

  * Fix `False` not being an acceptable env

  * Additional testcase for prefix being false from envvar

  * unset envvar_prefix after test
- Adhering to Github Community Standards (#175) [Bruno Rocha]
- Add note to release script. [Bruno Rocha]
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
