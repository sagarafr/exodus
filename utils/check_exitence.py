def check_existence(dictionary: dict, keys: list):
    """
    Check the existence of all key elements in dictionary with the keys list

    :param dictionary: dict to check all keys 
    :param keys: keys to check
    """
    return all(key in dictionary for key in keys) and len(dictionary) == len(keys)
