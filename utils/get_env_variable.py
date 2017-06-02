from os import environ


def get_os_variable(env_variable: list):
    variable = None
    for var in env_variable:
        if var in environ:
            variable = environ[var]
            break
    return variable


def get_os_auth_url():
    return get_os_variable(['OS_AUTH_URL'])


def get_os_password():
    return get_os_variable(['OS_PASSWORD'])


def get_os_token():
    return get_os_variable(['OS_TOKEN'])


def get_os_username():
    return get_os_variable(['OS_USERNAME'])


def get_os_tenant_id():
    return get_os_variable(['OS_TENANT_ID'])


def get_os_user_domain_name():
    return get_os_variable(['OS_DOMAIN_NAME'])


def get_os_credentials():
    return get_os_auth_url(), get_os_token(), get_os_username(), get_os_password(), get_os_user_domain_name(), get_os_tenant_id()
