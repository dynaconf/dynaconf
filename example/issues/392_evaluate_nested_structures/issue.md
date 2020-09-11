# [bug] LazyFormatted values don't get evaluated properly when they are not strings

* created by @cBournhonesque on 2020-08-17 22:20:30 +0000 UTC

**Describe the bug**
Values using @format don't get evaluated properly in data structures that are not strings.
Instead the returned value is `<dynaconf.utils.parse_conf.LazyFormat object at 0x105737a90>`.

**To Reproduce**
Steps to reproduce the behavior:

1. Having the following config files:

In `settings.toml`:

```
[default]
VAL = "val"
TEST = ["a", "@format {this.VAL}]
```


2. Having the following app code:


**/path/src/app.py**
```python
from dynaconf import settings
print(settings.TEST)
...
```



</details>

**Expected behavior**
The result should be `["a", "val"]`.
Instead the second value doesn't get lazily evaluated and I get: `["a", <dynaconf.utils.parse_conf.LazyFormat object at 0x105737a90>]`

To get the value of the second element, I would have to do `print(settings.TEST[1](settings))`

**Environment (please complete the following information):**
 - OS: MacOS



## Comments:

### comment by @vinayan3 on 2020-08-21 23:56:53 +0000 UTC

Hitting this with a dictionary
`settings.yaml`
```
DEV:
  USER_CONFIG:
    VALUE: foo
  SOME_DICT:
    VALUE: "@format {this.USER_CONFIG.VALUE}"
```
```
>> Config.from_env("DEV").SOME_DICT.VALUE
<dynaconf.utils.parse_conf.LazyFormat object at 0x7f53b53ca1d0>
```
