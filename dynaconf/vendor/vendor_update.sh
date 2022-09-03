# NOTES:
# WE ARE NOT TOUCHING ruamel/yaml or box libraries
# We update only click, toml and dotenv

rm -rf /tmp/dynaconf_vendoring
mkdir -p /tmp/dynaconf_vendoring

# For each library clone its repository into /tmp/dynaconf_vendoring/
git clone -b 8.1.3 https://github.com/pallets/click --depth 1 /tmp/dynaconf_vendoring/click
git clone -b 2.0.1 https://github.com/hukkin/tomli --depth 1 /tmp/dynaconf_vendoring/tomli
git clone -b v0.21.0 https://github.com/theskumar/python-dotenv --depth 1 /tmp/dynaconf_vendoring/python-dotenv

# For each library copy its source code to dynaconf/vendor

# click
rm -rf click
cp -r /tmp/dynaconf_vendoring/click/src/click click
# toml
rm -rf toml
cp -r /tmp/dynaconf_vendoring/tomli/src/tomli toml
# dotenv
rm -rf dotenv
cp -r /tmp/dynaconf_vendoring/python-dotenv/src/dotenv dotenv

echo "Some import paths must be manually resolved"
git grep "import click"
git grep "from click"
git grep "import toml"
git grep "from toml"
git grep "import dotenv"
git grep "from dotenv"
