from abc import ABC
from datetime import datetime

from .notifier import Notifier
from .async_notifier import AsyncNotifier, MetaDelayedNotifier
from .segment_locmem_client import SegmentLocMemClient


class SegmentNotifier(Notifier, ABC, metaclass=MetaDelayedNotifier):
    __slots__ = ('timestamp', 'user', )
    client_pool = {}
    event_id = None

    @classmethod
    def is_default_delayed(cls):
        return True

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        is_delayed = kwargs.pop('delayed', False)
        instance.__init__(*args, **kwargs)

        if is_delayed:
            # Get timestamp when the event was created by allow passing it or having a default one
            kwargs.setdefault('timestamp', instance.timestamp)
            return AsyncNotifier(*args, notifier_class=cls, **kwargs)
        else:
            return super().__new__(cls)

    def __init__(self, user=None, timestamp=None):
        self.timestamp = datetime.now() if not timestamp else timestamp
        self.user = user

    @property
    def segment_key(self):
        return None

    @property
    def client(self):
        return SegmentLocMemClient(None)

    @property
    def identify_properties(self):
        return None

    @property
    def uuid(self):
        return self.user.uuid if self.user else None

    @property
    def message(self):
        return {}

    def send(self):
        if not self.uuid:
            return

        if self.identify_properties:
            self.client.identify(self.uuid, self.identify_properties)

        if self.event_id:
            self.client.track(self.uuid, self.event_id, timestamp=self.timestamp, properties=self.message)
