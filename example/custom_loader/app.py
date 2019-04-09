from dynaconf import settings

print(
    'settings from sff file\n',
    open(settings.find_file('settings.sff')).read()
)

assert settings.NAME == "Bruno Rocha"
assert settings.EMAIL == 'bruno@rocha.com.from_env'

print("Name is:", settings.NAME)
print("Email is:", settings.EMAIL)

print(settings.get_fresh('NAME'))
