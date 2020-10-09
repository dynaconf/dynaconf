# [bug] Casting does not work with Box'd settings (eg dicts)

* created by @jhesketh on 2020-10-08 12:01:21 +0000 UTC

**Describe the bug**
Using any of the cast or "as_bool" etc methods do not work with nested/boxed settings.

**To Reproduce**

<details>
<summary> Python interpreter </summary>

```python

>>> settings.UPSTREAM_ROOK
<Box: {'BUILD_ROOK_FROM_GIT': 'TRUE'}>
>>> settings.UPSTREAM_ROOK.BUILD_ROOK_FROM_GIT
'TRUE'
>>> settings.as_bool('UPSTREAM_ROOK.BUILD_ROOK_FROM_GIT')
False
>>> settings.get('UPSTREAM_ROOK.BUILD_ROOK_FROM_GIT')
'TRUE'
>>> settings.get('UPSTREAM_ROOK.BUILD_ROOK_FROM_GIT', cast="@bool")
False

```
</details>

2. Having the following config files:

<!-- Please adjust if you are using different files and formats! -->

<details>
<summary> Config files </summary>

```
[upstream_rook]
build_rook_from_git = true
```


</details>


**Expected behavior**

`settings.as_bool('UPSTREAM_ROOK.BUILD_ROOK_FROM_GIT')` returns `True`.

