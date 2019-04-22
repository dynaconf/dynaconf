from dynaconf import settings

with open(settings.find_file("settings.sff")) as settings_file:
    print("settings from sff file\n", settings_file.read())

assert settings.NAME == "Bruno Rocha"
assert settings.EMAIL == "bruno@rocha.com.from_env"

print("Name is:", settings.NAME)
print("Email is:", settings.EMAIL)

print(settings.get_fresh("NAME"))
