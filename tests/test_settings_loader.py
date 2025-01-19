from __future__ import annotations

from dynaconf import Dynaconf
from dynaconf.loaders import settings_loader


def test_load_using_settings_loader(tmpdir):
    settings = Dynaconf(envvar_prefix=None)
    dummy_folder = tmpdir.mkdir("dummy1")

    dummy_folder.join("dummy_module.py").write('FOOB = "bar"')
    dummy_folder.join("__init__.py").write('print("initing dummy...")')

    settings_loader(settings, "dummy1.dummy_module")
    assert settings.exists("FOOB")
    assert settings.FOOB == "bar"


def test_load_using_settings_loader_with_environments(tmpdir):
    settings = Dynaconf(environments=True)
    dummy_folder = tmpdir.mkdir("dummy2")

    dummy_folder.join("dummy_module.py").write('FOOB = "bar"')
    dummy_folder.join("__init__.py").write('print("initing dummy...")')

    settings_loader(settings, "dummy2.dummy_module")

    assert settings.exists("FOOB")
    assert settings.FOOB == "bar"
    assert settings.current_env == "DEVELOPMENT"


def test_load_using_settings_loader_with_temporary_env(tmpdir):
    settings = Dynaconf(environments=True)
    dummya_folder = tmpdir.mkdir("dummya")

    dummya_folder.join("dummya_module.py").write('FOOB = "bar"')
    dummya_folder.join("__init__.py").write('print("initing dummya...")')

    # change the env on the fly only for this load
    settings_loader(settings, "dummya.dummya_module", env="PRODUCTION")

    assert settings.exists("FOOB")
    assert settings.FOOB == "bar"
    assert (
        settings.current_env == "DEVELOPMENT"
    )  # does not affect the current env


def test_load_using_settings_loader_with_multi_temporary_env(tmpdir):
    settings = Dynaconf(environments=True)
    dummyab_folder = tmpdir.mkdir("dummyab")

    dummyab_folder.join("dummyab_module.py").write('FOOB = "bar"')
    dummyab_folder.join("__init__.py").write('print("initing dummyab...")')

    dummyab_folder.join("quiet_dummyab_module.py").write("DEBUG = False")
    dummyab_folder.join("other_dummyab_module.py").write('FOOB = "zaz"')

    # change the env on the fly only for this load
    settings_loader(
        settings, "dummyab.dummyab_module", env="PRODUCTION,quiet,OTHER"
    )

    assert settings.exists("FOOB")
    assert settings.FOOB == "zaz"  # comes from other_dummyab_module.py
    assert (
        settings.current_env == "DEVELOPMENT"
    )  # does not affect the current env
    assert settings.DEBUG is False


def test_load_using_settings_loader_with_set_env(tmpdir):
    settings = Dynaconf(environments=True)
    settings.setenv("PRODUCTION")
    dummyb_folder = tmpdir.mkdir("dummyb")

    dummyb_folder.join("dummyb_module.py").write('FOOB = "bar"')
    dummyb_folder.join("__init__.py").write('print("initing dummyb...")')

    settings_loader(settings, "dummyb.dummyb_module")

    assert settings.exists("FOOB")
    assert settings.FOOB == "bar"
    assert settings.current_env == "PRODUCTION"


def test_load_using_settings_loader_with_one_env_named_file_module_path(
    tmpdir,
):
    settings = Dynaconf(environments=True)
    settings.setenv("PRODUCTION")
    dummyc_folder = tmpdir.mkdir("dummyc")

    dummyc_folder.join("dummyc_module.py").write('FOOB = "bar"')
    dummyc_folder.join("__init__.py").write('print("initing dummyc...")')

    dummyc_folder.join("production_dummyc_module.py").write('BAZ = "zaz"')

    settings_loader(settings, "dummyc.dummyc_module")

    assert settings.exists("FOOB")
    assert settings.FOOB == "bar"
    assert settings.current_env == "PRODUCTION"
    assert settings.BAZ == "zaz"


def test_load_using_settings_loader_with_one_env_named_file_file_path(tmpdir):
    settings = Dynaconf(environments=True)
    settings.setenv("PRODUCTION")
    dummyd_folder = tmpdir.mkdir("dummyd")

    dummyd_folder.join("dummyd_module.py").write('FOOB = "bar"')
    dummyd_folder.join("__init__.py").write('print("initing dummyd...")')

    dummyd_folder.join("production_dummyd_module.py").write('BAZ = "zaz"')

    settings_loader(settings, "dummyd/dummyd_module.py")

    assert settings.exists("FOOB")
    assert settings.FOOB == "bar"
    assert settings.current_env == "PRODUCTION"
    assert settings.BAZ == "zaz"


def test_load_using_settings_loader_with_one_env_named_file_module_path_multi_env(
    tmpdir,
):
    settings = Dynaconf(environments=True)
    settings.setenv("PRODUCTION,special")
    dummye_folder = tmpdir.mkdir("dummye")

    dummye_folder.join("dummye_module.py").write('FOOB = "bar"')
    dummye_folder.join("__init__.py").write('print("initing dummye...")')

    dummye_folder.join("production_dummye_module.py").write('BAZ = "zaz"')
    dummye_folder.join("special_dummye_module.py").write("DEBUG = False")

    settings_loader(settings, "dummye.dummye_module")

    assert settings.exists("FOOB")
    assert settings.FOOB == "bar"
    assert "PRODUCTION" in settings.current_env
    assert settings.BAZ == "zaz"
    assert settings.DEBUG is False  # comes from special_


def test_load_using_settings_loader_with_one_env_named_file_file_path_multi_env(
    tmpdir,
):
    settings = Dynaconf(environments=True)
    settings.setenv("PRODUCTION,special")
    dummyf_folder = tmpdir.mkdir("dummyf")

    dummyf_folder.join("dummyf_module.py").write('FOOB = "bar"')
    dummyf_folder.join("__init__.py").write('print("initing dummyf...")')

    dummyf_folder.join("production_dummyf_module.py").write('BAZ = "zaz"')
    dummyf_folder.join("special_dummyf_module.py").write("DEBUG = True")

    settings_loader(settings, "dummyf/dummyf_module.py")

    assert settings.exists("FOOB")
    assert settings.FOOB == "bar"
    assert "PRODUCTION" in settings.current_env
    assert settings.BAZ == "zaz"
    assert settings.DEBUG is True  # comes from special_
