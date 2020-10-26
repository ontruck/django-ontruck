import sys
import logging
from django.db import models
from django.contrib.contenttypes.models import ContentType

from .notifier import Notifier


logger = logging.getLogger(__name__)


def load_class(class_path):
    try:
        components = class_path.split('.')
        cls = components[-1]
        module = '.'.join(components[:-1])
        return getattr(sys.modules[module], cls)
    except (KeyError, TypeError, AttributeError) as err:
        logger.error(f'Cannot load class {class_path}\n{err}')

    return None


def to_primitives(*args, **kwargs):
    _args = list(args)
    _kwargs = kwargs
    primitive_indexes = {}
    primitive_keys = {}

    for index, obj in enumerate(_args):
        if isinstance(obj, models.Model):
            content_type_id = ContentType.objects.get_for_model(obj).id
            primitive_indexes[index] = content_type_id
            _args[index] = obj.pk

    _kwargs['primitive_indexes'] = primitive_indexes

    for key, obj in _kwargs.items():
        if isinstance(obj, models.Model):
            content_type_id = ContentType.objects.get_for_model(obj).id
            primitive_keys[key] = content_type_id
            _kwargs[key] = obj.pk

    _kwargs['primitive_keys'] = primitive_keys

    return (tuple(_args), _kwargs)


def from_primitives(*args, **kwargs):
    primitive_indexes = kwargs.pop('primitive_indexes', {})
    _args = list(args)
    _kwargs = kwargs

    for index, content_type_id in primitive_indexes.items():
        _args[index] = ContentType.objects.get_for_id(content_type_id).get_object_for_this_type(pk=_args[index])

    primitive_keys = kwargs.pop('primitive_keys', {})

    for key, content_type_id in primitive_keys.items():
        _kwargs[key] = ContentType.objects.get_for_id(content_type_id).get_object_for_this_type(pk=_kwargs[key])

    return (tuple(_args), _kwargs)


class AsyncNotifier(Notifier):
    __slots__ = ('notifier_class', 'notifier_args', 'notifier_kwargs',)
    default_queue = 'celery.notifications'

    def __init__(self, *args, **kwargs):
        kwargs.pop('client', None)  # skip client

        self.notifier_class = kwargs.pop('notifier_class', None)
        self.notifier_args = args
        self.notifier_kwargs = kwargs

    @property
    def notifier_class_path(self):
        return '.'.join([self.notifier_class.__module__, self.notifier_class.__name__])

    def send(self):
        if self.notifier_class:
            celery_opts = {
                'queue': self.default_queue,
                'shadow': self.notifier_class_path
            }

            if countdown := self.notifier_kwargs.get('countdown', None):
                celery_opts['countdown'] = countdown
            if eta := self.notifier_kwargs.get('eta', None):
                celery_opts['eta'] = eta

            # transform object instances into IDs
            _args, _kwargs = to_primitives(*self.notifier_args, **self.notifier_kwargs)

            return self.client.s(self.notifier_class_path, *_args, **_kwargs).apply_async(**celery_opts)


class MetaDelayedNotifier(type(Notifier)):
    def __call__(cls, *args, **kwargs):
        if 'delayed' not in kwargs and cls.is_default_delayed():
            kwargs['delayed'] = True
        notifier = cls.__new__(cls, *args, **kwargs)
        if not isinstance(notifier, AsyncNotifier):
            kwargs.pop('delayed', None)
            notifier.__init__(*args, **kwargs)
        return notifier
