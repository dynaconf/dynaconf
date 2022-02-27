#!/bin/bash
for direc in box click dotenv ruamel/yaml toml jinja2 markupsafe
do

   for eachfile in `ls dynaconf/vendor_src/$direc/*.py`
   do
      pyminify --remove-literal-statements $eachfile > ${eachfile/_src/''}
   done

done
