from abc import abstractmethod, ABC
import logging
import json
from django_ontruck.utils.retry import retry

from .mq_locmem_client import MQLocMemClient
from .notifier import Notifier
from .async_notifier import AsyncNotifier, MetaDelayedNotifier

logger = logging.getLogger(__name__)


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

    def __init__(self, queue_name, exchange_name=None, routing_key=None):
        self.queue_name = queue_name
        self.exchange_name = exchange_name or 'amq.direct'
        self.routing_key = routing_key or queue_name
        self.properties = None
        self.connection_manager = MQLocMemClient()  # fake client by default

    @property
    def channel(self):
        return self.client.make_channel(self.queue_name, self.exchange_name, self.routing_key)

    @property
    @abstractmethod
    def message(self):
        raise NotImplementedError()

    @retry(tries=3, delay=1, backoff=2)
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
