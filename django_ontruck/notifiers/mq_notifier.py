from abc import abstractmethod, ABC
import logging
import pika
import json
from django.conf import settings
from django_ontruck.utils.rabbitmq import RabbitMQConnectionManager
from django_ontruck.utils.retry import retry

from .mq_locmem_client import MQLocMemClient
from .notifier import Notifier
from .async_notifier import AsyncNotifier, MetaDelayedNotifier

logger = logging.getLogger(__name__)

max_retries = settings.ONTRUCK_RABBITMQ_MAX_RETRIES
sleep_time = settings.ONTRUCK_RABBITMQ_SLEEP_TIME


class MQNotifier(Notifier, ABC, metaclass=MetaDelayedNotifier):
    __slots__ = ('queue_name', 'exchange_name', 'routing_key', 'connection_manager', )

    @classmethod
    def is_default_delayed(cls):
        return True

    def __new__(cls, *args, **kwargs):
        is_delayed = kwargs.pop('delayed', False)

        if is_delayed:
            return AsyncNotifier(*args, notifier_class=cls, **kwargs)
        return super().__new__(cls)

    def __init__(self, queue_name, exchange_name=None, routing_key=None, connection_manager=None):
        self.queue_name = queue_name
        self.exchange_name = exchange_name or 'amq.direct'
        self.routing_key = routing_key or queue_name
        self.properties = None

        if not connection_manager:
            self.connection_manager = MQLocMemClient()  # fake client by default
        else:
            self.connection_manager = connection_manager

    @property
    def channel(self):
        return self.connection_manager.make_channel(self.queue_name, self.exchange_name, self.routing_key)

    @property
    @abstractmethod
    def message(self):
        raise NotImplementedError()

    @retry(tries=max_retries, delay=sleep_time, backoff=2)
    def send(self):
        try:
            if isinstance(self.message, dict):
                msg = json.dumps(self.message)
            elif self.message and self.message.is_valid():
                msg = json.dumps(self.message.serialize())
            else:
                return

            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=self.routing_key,
                body=msg,
                properties=self.properties)
        except Exception as e:
            logger.exception(e)
            raise e
