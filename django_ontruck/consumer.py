from abc import ABCMeta, abstractmethod
from celery import bootsteps
from kombu import Consumer, Exchange, Queue
from django.conf import settings


class ConsumerBase(bootsteps.ConsumerStep):
    __metaclass__ = ABCMeta

    @property
    @abstractmethod
    def queue_name(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def exchange_name(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def routing_key(self):
        raise NotImplementedError()

    @property
    def tag_prefix(self):
        return None

    @abstractmethod
    def perform(self, body, message):
        raise NotImplementedError('missing perform')

    def get_consumers(self, channel):
        queue = Queue(self.queue_name, Exchange(self.exchange_name), routing_key=self.routing_key)
        return [
            Consumer(
                channel,
                queues=[queue],
                callbacks=[self.handle_message],
                accept=['json', 'application/json'],
                tag_prefix=self.tag_prefix),
        ]

    def handle_message(self, body, message):
        try:
            self.perform(body, message)
        except Exception as e:
            message.requeue()

            if hasattr(settings, 'SENTRY_DSN'):
                from sentry_sdk import capture_exception

                capture_exception(e)
                return
