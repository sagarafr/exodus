from os import environ


def get_os_variable(env_variable: list):
    """
    Get the data inside the environment with key content in env_variable
    
    :param env_variable: list content all keys to find in the environment
    :return: str content the value of a environment key or None
    """
    variable = None
    for var in env_variable:
        if var in environ:
            variable = environ[var]
            break
    return variable


def get_os_auth_url():
    """
    Get the OS_AUTH_URL from the environment

    :return: str content the value of the OS_AUTH_URL environment key or None 
    """
    return get_os_variable(['OS_AUTH_URL'])


def get_os_password():
    """
    Get the OS_PASSWORD from the environment

    :return: str content the value of the OS_PASSWORD environment key or None 
    """
    return get_os_variable(['OS_PASSWORD'])


def get_os_token():
    """
    Get the OS_TOKEN from the environment

    :return: str content the value of the OS_TOKEN environment key or None 
    """
    return get_os_variable(['OS_TOKEN'])


def get_os_username():
    """
    Get the OS_USERNAME from the environment

    :return: str content the value of the OS_USERNAME environment key or None 
    """
    return get_os_variable(['OS_USERNAME'])


def get_os_tenant_id():
    """
    Get the OS_TENANT_ID from the environment

    :return: str content the value of the OS_TENANT_ID environment key or None 
    """
    return get_os_variable(['OS_TENANT_ID'])


def get_os_user_domain_name():
    """
    Get the OS_DOMAIN_NAME from the environment

    :return: str content the value of the OS_DOMAIN_NAME environment key or None 
    """
    return get_os_variable(['OS_DOMAIN_NAME'])


def get_os_credentials():
    """
    Get OpenStack credentials from the environment
    :return: str or None for the OS_AUTH_URL, OS_TOKEN, OS_USERNAME, OS_PASSWORD, OS_USER_DOMAIN_NAME and OS_TENANT_ID
    """
    return get_os_auth_url(), get_os_token(), get_os_username(), get_os_password(), get_os_user_domain_name(), get_os_tenant_id()
