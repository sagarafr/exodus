import logging


def debug(package_name):
    """
    Active the debug mode for a package_name

    :param package_name: package_name for the debug
    """
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('iso8601').setLevel(logging.WARNING)
    LOG = logging.getLogger(str(package_name))
    LOG.addHandler(logging.StreamHandler())
    LOG.setLevel(logging.DEBUG)
