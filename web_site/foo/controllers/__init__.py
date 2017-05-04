import uuid
import re
from collections import namedtuple

from celery import chain
from flask import current_app as app
import sqlalchemy.exc

from web_site.foo.extensions import db, cel
"""
from web_site.foo.models.persons import Person
from web_site.foo.tasks.persons import add_one_year
"""


class ControllerError(Exception):

    def __init__(self, message, context=None, kind=None):
        self.context = context or {}
        self.message = message.format(**self.context)
        if kind:
            self.kind = kind

    def __str__(self):
        return self.message


class NotFoundError(ControllerError):
    pass


EXCEPTIONS = ('NotFoundError',)

Paginator = namedtuple('Paginator',
                       ['objects', 'has_next', 'has_prev', 'page_current',
                        'page_next', 'page_prev', 'total_pages',
                        'total_objects'])


class ControllerMeta(type):
    """
    Metaclass used to provided class exceptions respecting inheritance.
    Example:
    >>> class A(metaclass=ModelMeta):
    ...     pass
    >>> class B(A):
    ...     pass
    >>> class C(A):
    ...     pass
    >>>
    >>> try:
    ...     raise B.NoObjectsReturned("b")
    ... except A.NoObjectsReturned as e:
    ...     print(e)
    b
    >>> try:
    ...     raise B.NoObjectsReturned("b")
    ... except C.NoObjectsReturned as e:
    ...     print(e)
    Traceback (most recent call last):
      File "<console>", line 2, in <module>
    NoObjectsReturned: b
    """

    def __new__(cls, name, bases, attrs):
        """Dynamically create a new class to inherit from.

        This function is fairly simple once you understood the type object
        See http://goo.gl/ka8voA for some explanations
        Makes exceptions in EXCEPTIONS appear in each Controller subclass.
        Creates a unique kind string in the exception to identify its type.
        """
        super_new = super(ControllerMeta, cls).__new__
        kind_prefix = name.split('Controller')[0]
        for exception in EXCEPTIONS:
            kind_suffix = re.sub('([A-Z]+)', r'_\1',
                                 exception.split('Error')[0])
            kind = kind_prefix + kind_suffix
            attrs[exception] = type(
                exception,
                tuple(getattr(x, exception) for x in bases
                      if hasattr(x, exception)) or (eval(exception),),
                {'kind': kind.upper()}
            )
        return super_new(cls, name, bases, attrs)


class Controller(metaclass=ControllerMeta):

    model_cls = None
    hidden_attributes = ()

    @classmethod
    def get(cls, id, filters=None, blacklist=False):
        obj = cls._get(id, filters)
        return cls.resource_to_dict(obj, blacklist)

    @classmethod
    def _get(cls, id, filters=None, with_lock=False):
        if filters is None:
            filters = {}
        err = cls.NotFoundError(
            'Could not find resource with id {id}',
            {'id': id}
        )

        try:
            uuid.UUID(id)
        except ValueError:
            # SQLAlchemy won't be happy is uuid is not well formatted
            raise err

        query = cls.model_cls.query.filter_by(id=id, **filters)
        if with_lock:
            query = query.with_lockmode('update')
        obj = query.first()

        if obj is None:
            raise err

        return obj

    @classmethod
    def resource_to_dict(cls, obj, blacklist=False):
        d = obj.to_dict()
        if blacklist:
            d = {k: v for k, v in d.items() if k not in cls.hidden_attributes}
        return d

    @classmethod
    def list(cls, filters, order_by=None, limit=None,
             reverse=None, blacklist=False):
        objs = cls._list(filters, order_by, limit,
                         reverse)
        return [cls.resource_to_dict(o, blacklist=blacklist) for o in objs]

    @classmethod
    def _list(cls, filters=None, order_by=None, limit=None,
              reverse=None):
        """Fetch a list or resources

        Additional filters on model can be given to reduce the list of results
        """
        if filters is None:
            filters = {}
        if order_by:
            order_attribute = getattr(cls.model_cls, order_by)
        else:
            order_attribute = cls.model_cls.created_at
        query = cls.model_cls.query

        query = query. \
            filter_by(**filters)

        query = query.order_by(
            order_attribute.desc() if reverse else order_attribute)
        if limit:
            query = query.limit(limit)
        return query.all()

    @classmethod
    def create(cls, data):
        return cls.resource_to_dict(cls._create(data))

    @classmethod
    def _create(cls, data):
        obj = cls.model_cls(**data)
        obj.check_integrity()
        db.session.add(obj)
        db.session.commit()
        app.logger.info('Created new {} {}'.format(
            cls.model_cls.__name__, obj.id
        ))
        return obj

    @classmethod
    def update(cls, id, data, **filters):
        return cls.resource_to_dict(cls._update(id, data, **filters))

    @classmethod
    def _update(cls, id, data, **filters):
        obj = cls._get(id, **filters)

        for key, value in data.items():
            setattr(obj, key, value)

        obj.check_integrity()

        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError as error:
            cls.handle_integrity_error(obj, error)
            raise error  # Raised again if no error raised in the handler.
        app.logger.info('Updated {} {}'.format(
            cls.model_cls.__name__, obj.id
        ))
        return obj

    @classmethod
    def delete(cls, id, **filters):
        return cls._delete(id, **filters)

    @classmethod
    def _delete(cls, id, **filters):
        """
        Delete specific object
        :return dict: deleted object dict
        """
        obj = cls._get(id, **filters)
        obj_dict = cls.resource_to_dict(obj)
        db.session.delete(obj)
        db.session.commit()
        return obj_dict

    @classmethod
    def schedule_task(cls, task_func, *args, **kwargs):
        task_result = task_func.delay(*args, **kwargs)
        if cel.conf.CELERY_ALWAYS_EAGER:
            # Tasks are already executed
            return []
        app.logger.info('Scheduled async task {} with args {} {}'.format(
            task_func.name, args, kwargs
        ))
        return [task_result.id]

    @classmethod
    def schedule_chain(cls, name, chain):
        app.logger.info('Scheduled async chain {}'.format(
            name,
        ))
        chain_result = chain()
        if cel.conf.CELERY_ALWAYS_EAGER:
            # Tasks are already executed
            return []
        return [chain_result.id]
