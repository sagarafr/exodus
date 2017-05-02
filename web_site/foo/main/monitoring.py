from . import main


@main.route('/mon/ping')
def ping():
    """Monitoring route, used to assess if the API is running."""
    return 'OK'


@main.route('/testing')
def testing():
    return 'YOLO\n'
