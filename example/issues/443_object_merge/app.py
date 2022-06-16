from __future__ import annotations

from dynaconf.utils import object_merge
from dynaconf.utils.boxing import DynaBox

existing_data = DynaBox(
    {
        "DATABASES": {
            "default": {
                "ENGINE": "django.db.backends.postgresql_psycopg2",
                "HOST": "localhost",
                "PASSWORD": "pulp",
                "NAME": "pulp",
                "USER": "pulp",
            }
        }
    }
)
assert existing_data["DATABASES"]["default"]["USER"] == "pulp"

new_data = DynaBox({"DATABASES": {"default": {"USER": "postgres"}}})
split_keys = ["DATABASES", "default", "USER"]
new = object_merge(old=existing_data, new=new_data, full_path=split_keys)

assert new["DATABASES"]["default"]["USER"] == "postgres"
assert new["DATABASES"]["default"]["NAME"] == "pulp"
assert new["DATABASES"]["default"]["PASSWORD"] == "pulp"
