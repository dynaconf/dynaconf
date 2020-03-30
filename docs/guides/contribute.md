# How to contribute

In github [repository](https://github.com/rochacbruno/dynaconf/) issues and Pull Request are welcomed!

- New implementations
- Bug Fixes
- Bug reports
- More examples of use in /example folder
- Documentation
- Feedback as issues and comments or joining #dynaconf on freenode
- Donation to rochacbruno [at] gmail.com in PayPal

## New implementations - Steps

1. Create and use a new virtualenv and install the requirements of the file requirements_dev.txt.
2. Install the pre-commit

    `pre-commit install --install-hooks`
3. During and after development run tests !

    `py.test -v --cov-config .coveragerc --cov=dynaconf -l tests/ --junitxml=junit/test-results.xml`
