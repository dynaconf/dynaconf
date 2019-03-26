from dynaconf import settings

assert settings.COLORS == [
    'green', 'yellow', 'blue', 'red', 'pink', 'green'
], settings.COLORS
print(settings.COLORS)
assert settings.FRUITS == [
    'orange', 'banana', 'apple', 'melon'
], settings.FRUITS
print(settings.FRUITS)
assert settings.DATABASE == {
    'host': 'server.com', 'user': 'admin', 'password': 's3cr4t', 'port': 666
}, settings.DATABASE
print(settings.DATABASE)
