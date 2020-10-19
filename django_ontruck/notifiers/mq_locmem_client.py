from django_ontruck import notifiers as module


class MQLocMemClient(object):
    def __init__(self, *args, **kwargs):
        if not hasattr(module, 'rt_outbox'):
            module.rt_outbox = []

    def make_channel(self, *args, **kwargs):
        return self

    def basic_publish(self, *args, **kwargs):
        return module.rt_outbox.append({'args': args, 'kwargs': kwargs})
