import logging


def debug(package_name):
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('iso8601').setLevel(logging.WARNING)
    LOG = logging.getLogger(str(package_name))
    LOG.addHandler(logging.StreamHandler())
    LOG.setLevel(logging.DEBUG)
