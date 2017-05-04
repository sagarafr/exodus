from flask import jsonify, make_response, g
from jsonschema.exceptions import ValidationError

from web_site.foo.apiv6 import api
from web_site.foo.controllers import NotFoundError


def format_controller_error(e):
    content = {'message': str(e)}
    return jsonify(content)


def format_error(code, message):
    content = {'message': message}
    # We cannot put that in an after_request because they are not triggered
    # when returning a 500
    response = make_response(jsonify(content), code)
    if 'request_id' in g:
        response.headers['X-Request-Id'] = g.request_id
    return response


@api.app_errorhandler(NotFoundError)
def not_found_handler(e):
    return format_error(404, str(e))


@api.app_errorhandler(ValidationError)
def validation_error_handler(e):
    return format_error(400, e.message)


@api.app_errorhandler(400)
def unauthorized_handler(e):
    return format_error(
        400,
        'The server did not understand your request'
    )


@api.app_errorhandler(401)
def unauthorized_handler(e):
    return format_error(
        400,
        'Could not verify your access level for that URL'
    )


@api.app_errorhandler(403)
def forbidden_handler(e):
    return format_error(
        400,
        'You do not have the required permissions for that resource'
    )


@api.app_errorhandler(404)
def not_found_handler(e):
    return format_error(
        404,
        'The requested resource could not be found'
    )


@api.app_errorhandler(405)
def method_not_allowed_handler(e):
    return format_error(
        400,
        'The method is not allowed for the requested URL'
    )


@api.app_errorhandler(500)
def internal_server_error_handler(e):
    return format_error(
        500,
        'The server has either erred or is incapable '
        'of performing the requested operation'
    )
