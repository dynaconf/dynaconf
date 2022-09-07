# Contributing

When contributing to this repository, please first discuss the change you wish to make via issue,
email, or any other method with the owners of this repository before making a change.

Please note we have a code of conduct, please follow it in all your interactions with the project.

This Diagram can help you understand visually what happens on Dynaconf: https://viewer.diagrams.net/?highlight=0000ff&edit=_blank&layers=1&nav=1&title=Dynaconf#Uhttps%3A%2F%2Fdrive.google.com%2Fuc%3Fid%3D11krXcDr67FGci_f36FZO-hiL08z4FuL9%26export%3Ddownload

## Pull Request Process

1. Ensure your local environment is set.
   1. Clone your own fork of this repo
   2. Activate a python3.6+ virtualenv
   3. Code
2. Update the `docs/guides/` related to your changes.
3. Update `tests_functional/` (editing or adding a new one related to your changes)
4. Ensure tests are passing (see below `make all`)
   1. This project uses `pre-commit` and `Black` for code styling and adequacy tests.
5. Commit, Push and make a Pull Request!


### Common Workflow:

```bash
# clone your fork of this repo
git clone git@github.com:{$USER}/dynaconf.git

# Add the upstream remote
git remote add upstream https://github.com/dynaconf/dynaconf.git

# Activate your Python Environment
python3.7 -m venv venv
source venv/bin/activate

# Install dynaconf for development
make all

# Checkout to a working branch
git checkout -b my_feature

# Open your favorite editor (VSCode for example)
code .

# After editing please rebase with upstream
git fetch upstream; git rebase upstream/master
# Fix any conflicts if any.

# Update docs/guides/ if needed
# Edit tests_functional/ if needed
# Create a new app in tests_functional/{your_example} and add it to Makefile.

# Then ensure everything is ok
make all

# Now commit your changes
git commit -am "Changed XPTO to fix #issue_number"

# Push to your own fork
git push -u origin HEAD

# Open github.com/dynaconf/dynaconf and send a Pull Request.
```

### Run integration tests

* "make all" do not run integration tests for Redis and Vault.
* If you want to run integration tests, make sure you have docker installed

```bash

# To install docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
<output truncated>

# To permit your user run docker commands without sudo
sudo usermod -aG docker {$USER}

# Run complete integration tests
make test_integration

# or Run functional example tests individually
make test_redis
make test_vault

```

## Code of Conduct

### Our Pledge

In the interest of fostering an open and welcoming environment, we as
contributors and maintainers pledge to making participation in our project and
our community a harassment-free experience for everyone, regardless of age, body
size, disability, ethnicity, gender identity and expression, level of experience,
nationality, personal appearance, race, religion, or sexual identity and
orientation.

### Our Standards

Examples of behavior that contributes to creating a positive environment
include:

* Using welcoming and inclusive language
* Being respectful of differing viewpoints and experiences
* Gracefully accepting constructive criticism
* Focusing on what is best for the community
* Showing empathy towards other community members

Examples of unacceptable behavior by participants include:

* The use of sexualized language or imagery and unwelcome sexual attention or
advances
* Trolling, insulting/derogatory comments, and personal or political attacks
* Public or private harassment
* Publishing others' private information, such as a physical or electronic
  address, without explicit permission
* Other conduct which could reasonably be considered inappropriate in a
  professional setting

### Our Responsibilities

Project maintainers are responsible for clarifying the standards of acceptable
behavior and are expected to take appropriate and fair corrective action in
response to any instances of unacceptable behavior.

Project maintainers have the right and responsibility to remove, edit, or
reject comments, commits, code, wiki edits, issues, and other contributions
that are not aligned to this Code of Conduct, or to ban temporarily or
permanently any contributor for other behaviors that they deem inappropriate,
threatening, offensive, or harmful.

### Scope

This Code of Conduct applies both within project spaces and in public spaces
when an individual is representing the project or its community. Examples of
representing a project or community include using an official project e-mail
address, posting via an official social media account, or acting as an appointed
representative at an online or offline event. Representation of a project may be
further defined and clarified by project maintainers.

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported by contacting the project team at `rochacbruno [at] gmail [dot] com`. All
complaints will be reviewed and investigated and will result in a response that
is deemed necessary and appropriate to the circumstances. The project team is
obligated to maintain confidentiality with regard to the reporter of an incident.
Further details of specific enforcement policies may be posted separately.

Project maintainers who do not follow or enforce the Code of Conduct in good
faith may face temporary or permanent repercussions as determined by other
members of the project's leadership.

### Attribution

This Code of Conduct is adapted from the [Contributor Covenant][homepage], version 1.4,
available at [http://contributor-covenant.org/version/1/4][version]

[homepage]: http://contributor-covenant.org
[version]: http://contributor-covenant.org/version/1/4/
