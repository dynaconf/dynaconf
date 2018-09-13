.. dynaconf documentation master file, created by
   sphinx-quickstart on Sun Oct 15 16:27:42 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

**dynaconf** a layered configuration system for Python applications -
with strong support for `12-factor applications`_
and extensions for `Flask`_ and `Django`_.

Release v\ |version|. (`Installation`_)


.. image:: https://img.shields.io/pypi/l/dynaconf.svg
    :target: https://pypi.org/project/dynaconf/

.. image:: https://img.shields.io/pypi/wheel/dynaconf.svg
    :target: https://pypi.org/project/dynaconf/

.. image:: https://img.shields.io/pypi/pyversions/dynaconf.svg
    :target: https://pypi.org/project/dynaconf/

.. image:: https://img.shields.io/pypi/v/dynaconf.svg
    :target: https://pypi.org/project/dynaconf/

.. image:: https://api.codacy.com/project/badge/Grade/5074f5d870a24ddea79def463453545b    
    :target: https://www.codacy.com/app/rochacbruno/dynaconf?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=rochacbruno/dynaconf&amp;utm_campaign=Badge_Grade

.. image:: https://img.shields.io/badge/Say%20Thanks!-🦉-1EAEDB.svg
    :target: https://saythanks.io/to/rochacbruno

Features
--------

- Strict separation of settings from code (following `12-factor applications`_ Guide).
- Define comprehensive default values.
- Store parameters in multiple file formats (**.toml**, .json, .yaml, .ini and .py).
- Sensitive **secrets** like tokens and passwords can be stored in `safe places`_ like `.secrets` file or `vault server`.
- Parameters can optionally be stored in `external services`_ like Redis server.
- Simple `feature flag`_ system.
- Layered **[environment]** system.
- `Environment variables`_ can be used to override parameters.
- Support for `.env` files to automate the export of environment variables.
- Correct data types (even for environment variables).
- Have **only one** `canonical settings module`_ to rule all your instances.
- Drop in extension for `Flask`_ `app.config` object.
- Drop in extension for `Django`_ `conf.settings` object.
- Powerful **$ dynaconf** `CLI`_ to help you manage your settings via console.
- Customizable `Validation`_ System to ensure correct config parameters.
- Allow the change of **dynamic** parameters on the fly without the need to redeploy your application.


.. aafig::
    :aspect: 60
    :scale: 100
    :proportional:

    DDDDD  Y   Y N    N  AAAA   CCCCC  OOOO  N    N FFFFFF                                                                
    D    D YY YY NN   N AA  AA C      O    O NN   N F                                                              
    D    D  YYY  NNNN N A    A C      O    O NNNN N FFFF                                                           
    D    D   Y   N NNNN AAAAAA C      O    O N NNNN F                                                            
    D    D   Y   N   NN A    A C      O    O N   NN F                                                            
    DDDDD    Y   N    N A    A  CCCCC  OOOO  N    N F                                                                                                           



.. toctree::
   :maxdepth: 2
   :caption: Contents:

   guides/usage
   guides/sensitive_secrets
   guides/environment_variables
   guides/accessing_values
   guides/cli
   guides/external_storages
   guides/configuration
   guides/advanced_usage
   guides/feature_flag
   guides/validation
   guides/flask
   guides/django
   guides/testing
   guides/extend
   guides/contribute
   guides/examples
   guides/credits
   guides/alternatives
   Module reference <reference/modules>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _12-factor applications: https://12factor.net/config
.. _flask: guides/flask.html
.. _django: guides/django.html
.. _safe places: guides/sensitive_secrets.html 
.. _external services: guides/external_storages.html
.. _feature flag: guides/feature_flag.html 
.. _environment variables: guides/environment_variables.html 
.. _canonical settings module: guides/usage.html 
.. _cli: guides/cli.html 
.. _validation: guides/validation.html
.. _Installation: guides/usage.html
