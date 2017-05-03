def check_existence(dictionary: dict, keys: list):
    return all(key in dictionary for key in keys) and len(dictionary) == len(keys)
