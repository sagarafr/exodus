from getpass import getpass


def ask_credential(elements: list):
    """
    Ask credentials
    :param elements: list of tuple. Tuple must follow this schema (bool, str)
     if bool is true then it's a password else it's not
    :return: answers
    """
    answers = []
    for element in elements:
        if isinstance(element, tuple):
            sentence = element[1] if element[1] is not None and element[1] != "" else ""
            if not element[0]:
                answer = input(sentence)
            else:
                answer = getpass(sentence) if sentence != "" else getpass()
            answers.append(answer)
        else:
            raise TypeError("Each element of list must be a tuple")
    return answers
