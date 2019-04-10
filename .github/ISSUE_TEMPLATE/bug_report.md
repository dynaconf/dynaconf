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

/path/
...../folder/...
# please provide your folder structure here

```
</details>

2. Having the following config files:

<!-- Please replace if you are using different files and formats! -->

<details>
<summary> Config files </summary>

**/path/.env**
```bash
Your .env content here
```

and

/path/settings.toml
```toml
[default]
```

</details>

**Expected behavior**
A clear and concise description of what you expected to happen.

**Debug output**

<details>
<summary> Debug Output </summary>

```bash

export `DEBUG_LEVEL_FOR_DYNACONF=true` reproduce your problem and paste the output here

```

</details>

**Environment (please complete the following information):**
 - OS: [e.g. iOS]
 - Dynaconf Version [e.g. 2.0.0/source]

**Additional context**
Add any other context about the problem here.
