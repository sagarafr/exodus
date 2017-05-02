import logging
from logging.handlers import QueueHandler, QueueListener
import queue
import time

import celery.signals
import flask


def setup_loggers(app):
    """Setup loggers for a production environment"""
    # Flask lazily initializes its logger, it must be called here so we can
    # change its configuration
    _ = app.logger

    for logger_name in ('', app.name, 'celery'):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)

        # Clean all existing handlers
        logger.handlers = list()

    # Add our handlers
    for handler in get_handlers_from_config(app.config['LOGGERS']):
        logging.getLogger().addHandler(handler)

    # Add a custom log for each Flask request
    flask.request_started.connect(log_prerequest, app)
    flask.request_finished.connect(log_postrequest, app)

    # Remove Gunicorn access log to not get the info twice
    logging.getLogger('gunicorn.access').handlers = []

    @celery.signals.setup_logging.connect
    def setup_logging(loglevel, logfile, format, colorize, **kwargs):
        """Hack to prevent Celery from messing with loggers.

        See https://github.com/celery/celery/issues/1867
        """
        pass


def log_prerequest(app, **kwargs):
    flask.g.request_start_time = time.time()
    flask.g.is_admin = False


def log_postrequest(app, **kwargs):
    response = kwargs['response']
    execution_time = time.time() - flask.g.get('request_start_time')
    execution_time = round(execution_time, 3)
    msg = '{} {} {} {}s'.format(
        flask.request.method, flask.request.path,
        response.status_code, execution_time
    )
    app.logger.info(
        msg,
        extra={
            'execution_time': execution_time,
            'response_status_code': response.status_code,
            'response_content_length': response.content_length,
        }
    )


def get_handlers_from_config(config):
    """Read config['LOGGERS'] and generate the corresponding handlers"""
    handlers = list()
    async_handlers = list()
    for handler_type, handler_config in config.items():
        handler = None
        if handler_type == 'syslog':
            handler = _get_syslog_handler(handler_config)
        elif handler_type == 'stdout':
            handler = _get_stdout_handler(handler_config)
        elif handler_type == 'file':
            handler = _get_file_handler(handler_config)
        elif handler_type == 'ltsv':
            handler = _get_ltsv_handler(handler_config)

        if handler:
            handler.setLevel(getattr(logging, handler_config['level'].upper()))
            if handler_config['async']:
                async_handlers.append(handler)
            else:
                handlers.append(handler)

    if async_handlers:
        que = queue.Queue(-1)
        queue_handler = QueueHandler(que)
        handlers.append(queue_handler)
        listener = QueueListener(que, *async_handlers,
                                 respect_handler_level=True)
        listener.start()

    return handlers


def _get_syslog_handler(logger_config):
    """Get a syslog handler.

    If 'device' is set it will use this device as syslog address,
    otherwise it will send to 'host':'port' using either TCP or UDP as
    defined in 'transport'.
    """
    from logging.handlers import SysLogHandler
    from socket import SOCK_DGRAM, SOCK_STREAM
    if logger_config.get('device', False):
        return SysLogHandler(address=logger_config['device'])
    address = (logger_config['host'], logger_config['port'])
    socktype = SOCK_STREAM
    if logger_config['transport'] == 'UDP':
        socktype = SOCK_DGRAM
    handler = SysLogHandler(
        address=address,
        socktype=socktype,
        facility=SysLogHandler.LOG_USER
    )
    return handler


def _get_stdout_handler(logger_config):
    from logging import StreamHandler
    from sys import stdout
    handler = StreamHandler(stream=stdout)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    return handler


def _get_ltsv_handler(logger_config):
    from djehouty.libltsv.handlers import LTSVTCPSocketHandler
    handler = LTSVTCPSocketHandler(
        host=logger_config['host'],
        port=logger_config['port'],
        use_tls=logger_config['use_tls'],
        static_fields=logger_config['static_fields']
    )
    return handler


def _get_file_handler(logger_config):
    from logging.handlers import RotatingFileHandler
    handler = RotatingFileHandler(
        filename=logger_config['file_name'],
        maxBytes=logger_config['max_bytes'],
        backupCount=logger_config['backups']
    )
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    return handler


class TaskLoggerAdapter(logging.LoggerAdapter):
    """LoggerAdapter to be used within tasks."""
    def process(self, msg, kwargs):
        data = dict()

        task = kwargs.pop('task', None)
        if task:
            data.update({
                'task_id': getattr(task.request, 'id', None),
                'task_name': getattr(task.request, 'task', None),
                'task_args': getattr(task.request, 'args', None),
                'task_reply_to': getattr(task.request, 'reply_to', None),
                'task_retries': getattr(task.request, 'retries', None)
            })

        extra = kwargs.setdefault("extra", {})
        for key in data:
            extra.setdefault(key, data[key])

        return msg, kwargs


class FlaskLoggerAdapter(logging.LoggerAdapter):
    """LoggerAdapter to be used within Flask requests."""
    def process(self, msg, kwargs):
        import flask
        from flask import request
        data = dict()

        # For web API
        if flask.has_request_context():
            data = {
                'request_method': request.method,
                'request_remote_addr': request.remote_addr,
                'request_endpoint': request.endpoint,
                'request_url': request.url,
                'request_path': request.path,
                'request_query_args': request.args.to_dict(flat=False),
                'request_user_agent': request.user_agent.string
            }

        extra = kwargs.setdefault("extra", {})
        for key in data:
            extra.setdefault(key, data[key])

        return msg, kwargs

    @property
    def name(self):
        return self.logger.name
