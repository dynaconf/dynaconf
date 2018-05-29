# Accessing parameters

Dynaconf offers different ways to access settings parameters

Assuming the following `settings.toml` file

```ini
[default]
host = "server"
port = 5555
auth = {user="admin", passwd="1234"}
```

## As attributes (dot notation)

Using dot notation

```python
settings.HOST
```

> Raises: **AttributeError** if not defined

## As dictionary [item]

Using item access

```python
settings['PORT']
```

> Raises: **KeyError** if not defined

## Default values (get)

Using dict style get

```python
settings.get('TIMEOUT', 300)
```

> Returns the default (300) if not defined

## Forcing type casting

```python
settings.as_int('PORT')
```

Available casts:

- as_int
- as_float
- as_bool
- as_json

## Boxed values

In Dynaconf values are Boxed, it means the dot notation can also be used to access dictionary members, example:

settings.toml

```ini
[default]
mysql = {host="server.com", port=3600, auth={user="admin", passwd=1234}}
```

You can now access

```python
from dynaconf import settings

connect(
    host=settings.MYSQL.host,
    port=settings.MYSQL.port,
    username=settings.MYSQL.auth.user,
    passwd=settings.MYSQL.auth.get('passwd'),
)
```
