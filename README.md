[![Dynaconf](https://raw.githubusercontent.com/rochacbruno/dynaconf/master/docs/_static/logo_big.svg?sanitize=true)](http://dynaconf.readthedocs.io)

> **dynaconf** - The **dyna**mic **conf**igurator for your Python Project

[![MIT License](https://img.shields.io/badge/license-MIT-007EC7.svg?style=flat-square)](/LICENSE) [![PyPI](https://img.shields.io/pypi/v/dynaconf.svg)](https://pypi.python.org/pypi/dynaconf) [![PyPI](https://img.shields.io/pypi/pyversions/dynaconf.svg)]() ![PyPI - Downloads](https://img.shields.io/pypi/dm/dynaconf.svg?label=pip%20installs&logo=python) [![Build Status](https://dev.azure.com/rochacbruno/dynaconf/_apis/build/status/rochacbruno.dynaconf?branchName=master)](https://dev.azure.com/rochacbruno/dynaconf/_build/latest?definitionId=1&branchName=master) ![Azure DevOps builds (branch)](https://img.shields.io/azure-devops/build/rochacbruno/3e08a9d6-ea7f-43d7-9584-96152e542071/1/master.svg?label=windows%20build&logo=windows) ![Azure DevOps builds (branch)](https://img.shields.io/azure-devops/build/rochacbruno/3e08a9d6-ea7f-43d7-9584-96152e542071/1/master.svg?label=linux%20build&logo=linux) [![codecov](https://codecov.io/gh/rochacbruno/dynaconf/branch/master/graph/badge.svg)](https://codecov.io/gh/rochacbruno/dynaconf) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/5074f5d870a24ddea79def463453545b)](https://www.codacy.com/app/rochacbruno/dynaconf?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=rochacbruno/dynaconf&amp;utm_campaign=Badge_Grade) ![GitHub issues](https://img.shields.io/github/issues/rochacbruno/dynaconf.svg) ![GitHub stars](https://img.shields.io/github/stars/rochacbruno/dynaconf.svg) ![GitHub Release Date](https://img.shields.io/github/release-date/rochacbruno/dynaconf.svg) ![GitHub commits since latest release](https://img.shields.io/github/commits-since/rochacbruno/dynaconf/latest.svg) ![GitHub last commit](https://img.shields.io/github/last-commit/rochacbruno/dynaconf.svg) [![Code Style Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black/)

**dynaconf** a layered configuration system for Python applications -
with strong support for [12-factor applications](https://12factor.net/config)
and extensions for **Flask** and **Django**.

**Read the Full Documentation at**: http://dynaconf.readthedocs.io/


# Top Contributors

[![](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/images/0)](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/links/0)[![](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/images/1)](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/links/1)[![](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/images/2)](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/links/2)[![](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/images/3)](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/links/3)[![](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/images/4)](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/links/4)[![](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/images/5)](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/links/5)[![](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/images/6)](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/links/6)[![](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/images/7)](https://sourcerer.io/fame/rochacbruno/rochacbruno/dynaconf/links/7)

# Features

- Strict separation of settings from code (following [12-factor applications](https://12factor.net/config) Guide).
- Define comprehensive default values.
- Store parameters in multiple file formats (**.toml**, .json, .yaml, .ini and .py).
- Sensitive **secrets** like tokens and passwords can be stored in safe places like `.secrets` file or `vault server`.
- Parameters can optionally be stored in external services like Redis server.
- Simple **feature flag** system.
- Layered **[environment]** system.
- Environment variables can be used to override parameters.
- Support for `.env` files to automate the export of environment variables.
- Correct data types (even for environment variables).
- Have **only one** canonical settings module to rule all your instances.
- Drop in extension for **Flask** `app.config` object.
- Drop in extension for **Django** `conf.settings` object.
- Powerful **$ dynaconf** CLI to help you manage your settings via console.
- Customizable **Validation** System to ensure correct config parameters.
- Allow the change of **dyna**mic parameters on the fly without the need to redeploy your application.

## Read the docs

**Documentation**: http://dynaconf.readthedocs.io/

```
██████╗ ██╗   ██╗███╗   ██╗ █████╗  ██████╗ ██████╗ ███╗   ██╗███████╗
██╔══██╗╚██╗ ██╔╝████╗  ██║██╔══██╗██╔════╝██╔═══██╗████╗  ██║██╔════╝
██║  ██║ ╚████╔╝ ██╔██╗ ██║███████║██║     ██║   ██║██╔██╗ ██║█████╗
██║  ██║  ╚██╔╝  ██║╚██╗██║██╔══██║██║     ██║   ██║██║╚██╗██║██╔══╝
██████╔╝   ██║   ██║ ╚████║██║  ██║╚██████╗╚██████╔╝██║ ╚████║██║
╚═════╝    ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝
```
