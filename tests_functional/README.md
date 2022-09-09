# Functional tests

Functional tests reproduces a use case or reproduce a bug or ensure a fix.

Functional tests runs on CI by calling `tests_functcional/runtests.py` script
this script is called when you run `make test_functional` in the root of the
repository.

This script walks through the `tests_functional` directory and runs all then
for every subdirectory it looks for one of the following files in order:

- Makefile
- test.sh
- test.py
- app.py
- program.py
- manage.py

The first found file will be executed via `subprocess.check_call` and the execution context
will be

- cwd: The subdirectory and then it will try to run also from the parent folder.
- env: os.environ + variables defined on `env.toml` file if it exists.

## How to assert in a test?

**Makefile** or **test.sh**

If the test is executed on the shell level, you can ensure it returns `0` as exit code.

**Ex:** On a makefile or test.sh you can do `python file.py | grep "something"` and it will return `0` if the grep found the string.

**test.py** or **app.py**

Tests executed on Python level is executed via `python filename.py` so anything that returns `0` as exit code will be considered a success.

**Ex:** `assert settings.KEY == "value"` will return `0` as exit code if the assertion is true.


**manage.py** (Django)

On a Django application, if no other test file is found such as (Makefile, test.sh) then runner will call `python manage.py test` with no arguments.

> **NOTE** to use pytest or more flexibility on command call please call it from the **Makefile** (test target) or **test.sh**, the only important thing is that the command returns `0` as exit code on success.

## Envvars

Environment variables are very important for Dynaconf so
most of the functional tests will need to customize those
there are 2 ways:

- Write a `.env` file and then pass `load_dotenv=True` to Dynaconf constructor.
- Use `env.toml` file to define environment variables, **IMPORTANT** that this file has only upper case keys and all values are strings: `THING = "value"`.

## Skipping functional tests

ON the `skipfile.toml` you can define a list of folder names to skip depending on the platform.

```toml
nt = ["tests_to_skip_on_windows"]
posix = ["tests_to_skip_on_linux"]
macos = ["tests_to_skip_on_macos"]
```

Those names matches `os.name` for the platform.


## How to add a new test?

> **NOTE**: Give your functional test example folder a meaningful name, for example `test_django_with_yaml/` or `test_feature_x_works_with_y_enabled/`


1. Create a new folder under `tests_functional`:
   ```console
   $ mkdir tests_functional/my_test
   ```
   > **IMPORTANT**!!!! if your test is to reproduce an issue, please add it to `tests_functional/issues/` folder, for example `tests_functional/issues/999_launching_a_rocket/`

2. Go to that folder:
   ```console
   $ cd tests_functional/my_test
   # or
   $ cd tests_functional/issues/999_launching_a_rocket
   ```


3. Create an `app.py`:

   ```python
   from dynaconf import Dynaconf
   settings = Dynaconf(
       envvar_prefix="MYAPP",
       settings_files=["settings.toml"],
       load_dotenv=True,
       # add parameters matching your use case
   )

   assert settings.KEY == "value"
   # Add things needed to assert your test case
   ```
   > **NOTE** Ensure you have the needed assertions at the end of the file.

3. Create needed artifacts for the test to run:
    ```console
    $ touch settings.toml
    $ touch .env
    ```
    Optionally
    ```console
    $ touch env.toml
    ```
4. If you need more flexibility to call the command or you have to pass extra envvars, do extra checks or connect services please use a `Makefile` or a `test.sh`
    ```console
    $ touch Makefile
    ```
    ```makefile
    test:
        python app.py
    ```
    or
    ```console
    $ touch test.sh
    ```
    ```bash
    #!/usr/bin/env bash
    python app.py | grep "something"
    ```

> **TIP** If you need multiple variations of the same structure with fewer changes, you can create subfolders with the same structure.
