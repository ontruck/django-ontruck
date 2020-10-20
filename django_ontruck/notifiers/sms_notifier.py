from abc import abstractmethod
from .notifier import Notifier
from .async_notifier import AsyncNotifier, MetaDelayedNotifier


class SMSNotifier(Notifier, metaclass=MetaDelayedNotifier):
    __slots__ = ('phone',)

    @classmethod
    def is_default_delayed(cls):
        return True

    def __new__(cls, *args, **kwargs):
        is_delayed = kwargs.pop('delayed', False)

        if is_delayed:
            return AsyncNotifier(*args, notifier_class=cls, **kwargs)
        else:
            return super().__new__(cls)

    def __init__(self, phone):
        self.phone = phone

    @property
    @abstractmethod
    def client(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def message(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def sender_name(self):
        raise NotImplementedError()

    def send(self):
        smsparams = {
            'to': self.phone,
            'message': self.message,
            'from_': self.sender_name,
        }

        return self.client.sms.send(**smsparams)
