import boto3
import botocore
from dynaconf.utils import build_env_list
from dynaconf import cli

IDENTIFIER = "ssm"

SSM_ERRORS_FATAL = False

ssm_client = boto3.client('ssm')

cli.WRITERS.append('ssm')


def load_env(obj, env):
    path = f'/{env}/'
    obj.logger.debug(f'path: {path}')

    paginator = ssm_client.get_paginator(
        'get_parameters_by_path',
    ).paginate(
        Path=path,
        Recursive=True,
        WithDecryption=True,
    )

    try:
        parameters = [
            param
            for page in paginator
            for param in page['Parameters']
        ]
    except botocore.exceptions.ClientError as exc:
        obj.logger.info(str(exc))
        if SSM_ERRORS_FATAL:
            raise exc
        return

    for param in parameters:
        name = param['Name'].replace(path, '').upper()
        obj.logger.info(f'Setting {name} from {param["Name"]}')
        obj.set(
            name,
            param['Value'],
        )


def load(obj, env=None, silent=True, key=None, filename=None):
    env_list = build_env_list(obj, env)
    for env in env_list:
        load_env(obj, env)


def write(obj, data=None, **kwargs):
    """Write a value in to loader source

    :param obj: settings object
    :param data: vars to be stored
    :param kwargs: vars to be stored
    :return:
    """
    if obj.SSM_ENABLED_FOR_DYNACONF is False:
        raise RuntimeError(
            "SSM is not configured \n"
            "export SSM_ENABLED_FOR_DYNACONF=true\n"
            "and configure the SSM_FOR_DYNACONF_* variables"
        )

    path = "/".join([obj.SSM_PATH_FOR_DYNACONF, obj.current_env.lower()])
    print(path, data)

    """
    ssm_client.put_parameter(
        Name=path,
        Value=data,
        Type='SecureString',
    )
    """
