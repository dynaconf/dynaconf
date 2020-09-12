from dynaconf import Dynaconf

settingsenv = Dynaconf(environments=True)
settings = Dynaconf(TEST_KEY="test_value", ANOTHER_KEY="another_value")
