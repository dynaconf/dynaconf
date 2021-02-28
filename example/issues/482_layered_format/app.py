from dynaconf import Dynaconf

settings_files = ["settings.toml", "other.toml"]

settings = Dynaconf(settings_files=settings_files)

expected_value = "s3a://kewl_bucket"

assert settings.s3_url == expected_value
assert settings.s3_url1 == expected_value
assert settings.s3_url2 == expected_value
assert settings.s3_url3 == expected_value

assert settings["s3_url"] == expected_value
assert settings["S3_URL"] == expected_value

assert settings.get("s3_url", default="s3://default") == expected_value
assert settings.get("S3_URL", default="s3://default") == expected_value

assert settings("s3_url", cast="@str") == expected_value
assert settings("S3_URL", cast="@str") == expected_value


print(settings.s3_url)
print(settings.S3_URL)

print(settings["s3_url"])
print(settings["S3_URL"])
