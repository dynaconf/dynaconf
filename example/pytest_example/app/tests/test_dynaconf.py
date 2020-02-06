from app import return_a_value


def test_dynaconf_is_in_testing_env():
    assert return_a_value() == "On Testing"
