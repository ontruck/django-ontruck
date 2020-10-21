from abc import ABC, abstractmethod
from datetime import datetime

from .notifier import Notifier
from .async_notifier import AsyncNotifier, MetaDelayedNotifier
from .slack_locmem_client import SlackLocMemClient


class SlackNotifier(Notifier, ABC, metaclass=MetaDelayedNotifier):
    slack_client = None

    @classmethod
    def is_default_delayed(cls):
        return True

    def __new__(cls, *args, **kwargs):
        is_delayed = kwargs.pop('delayed', False)

        if is_delayed:
            return AsyncNotifier(*args, notifier_class=cls, **kwargs)
        else:
            return super().__new__(cls)

    def __init__(self, timestamp=None):
        self.timestamp = datetime.now() if not timestamp else timestamp
        SlackNotifier.slack_client = SlackLocMemClient()

    @property
    @abstractmethod
    def channel(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def country_code(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def message(self):
        raise NotImplementedError()

    @property
    def attachments(self):
        return None

    def send(self):
        if not self.channel or not self.message:
            return

        kwargs = {}

        if self.attachments:
            kwargs['as_user'] = True
            kwargs['attachments'] = self.attachments

        self.client.chat.post_message(self.channel, self.message, link_names=True, **kwargs)
