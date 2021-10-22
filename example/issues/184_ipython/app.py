from dynaconf import Dynaconf

settings = Dynaconf(**options)

print(settings.ENV_FOR_DYNACONF)

assert settings.ENV_FOR_DYNACONF == "WORKS_ON_PYTHON_AND_IPYTHON"
