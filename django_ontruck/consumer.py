from abc import ABCMeta, abstractmethod
import json
import logging
from celery import bootsteps
from kombu import Consumer, Exchange, Queue
from django.conf import settings


logger = logging.getLogger(__name__)


class ConsumerBase(bootsteps.ConsumerStep):
    __metaclass__ = ABCMeta
    serializer_class = None
    use_case_class = None

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

    def perform(self, body, message):
        if isinstance(body, str):
            body = json.loads(body)

        if self.serializer_class and self.use_case_class:
            serializer = self.serializer_class(data=body)

            if serializer.is_valid():
                use_case = self.use_case_class()
                use_case.execute(command=serializer.validated_data)

                message.ack()
            else:
                message.reject()
                logger.error(f"Failed to process message {serializer.errors=}")
        else:
            raise NotImplementedError(
                'You have to specify a serializer_class and a use_case_class or implement perform method'
            )

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
