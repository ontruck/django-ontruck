import logging
from django_ontruck import notifiers as module

logger = logging.getLogger(__name__)


class SmsLocMemClient(object):

    class Sms(object):

        def send(self, *args, **kwargs):
            module.sms_outbox.append({'args': args, 'kwargs': kwargs})
            logger.info("SMS to %s\n%s", kwargs['to'], kwargs['message'])

    def __init__(self, *args, **kwargs):
        self._sms = self.Sms()
        if not hasattr(module, 'sms_outbox'):
            module.sms_outbox = []

    @property
    def sms(self, *args, **kwargs):
        return self._sms
