---
name: Bug report
about: Create a report to help us improve
title: "[bug]"
labels: bug
assignees: ''

---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:

1. Having the following folder structure

<!-- Describe or use the command `$ tree -v` and paste below -->

<details>
<summary> Project structure </summary>

```bash

# /path/
# ...../folder/...
# please provide your folder structure here

```
</details>

2. Having the following config files:

<!-- Please adjust if you are using different files and formats! -->

<details>
<summary> Config files </summary>

**/path/.env**
```bash
Your .env content here
```

and

**/path/settings.toml**
```toml
[default]
```

</details>

3. Having the following app code:

<details>
<summary> Code </summary>

**/path/src/app.py**
```python
from dynaconf import settings
...
```

</details>

4. Executing under the following environment

<details>
<summary> Execution </summary>

```bash
# other commands and details?
# virtualenv activation?

$ python /path/src/app.py
```

</details>

**Expected behavior**
A clear and concise description of what you expected to happen.

**Environment (please complete the following information):**
 - OS: [e.g. Linux/Fedora29, Windows/x.x.x, Linux/Ubuntu16.x]
 - Dynaconf Version [e.g. 2.0.0/source]
 - Frameworks in use (Flask, Django? versions..)

**Additional context**
Add any other context about the problem here.
