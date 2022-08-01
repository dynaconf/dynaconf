#!/bin/bash
python -c 'from my_app import settings; assert settings.server.version.release == "6.10"'
python -c 'from my_app import settings; assert settings.server.deploy_arguments.to_dict() == {"deploy_sat_version": "6.10", "deploy_snap_version": "22", "deploy_rhel_version": "7"}'
export MYAPP_SERVER__VERSION__RELEASE="7.2"
python -c 'from my_app import settings; assert settings.server.version.release == 7.2'
python -c 'from my_app import settings; assert settings.server.deploy_arguments.to_dict() == {"deploy_sat_version": "7.2", "deploy_snap_version": "22", "deploy_rhel_version": "7"}, settings.server.deploy_arguments'
unset MYAPP_SERVER__VERSION__RELEASE
