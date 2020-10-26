from abc import abstractmethod
from .notifier import Notifier
from .sms_locmem_client import SmsLocMemClient
from .async_notifier import AsyncNotifier, MetaDelayedNotifier


class SMSNotifier(Notifier, metaclass=MetaDelayedNotifier):
    __slots__ = ('phone_number',)
    async_class = AsyncNotifier

    @classmethod
    def is_default_delayed(cls):
        return True

    def __new__(cls, *args, **kwargs):
        is_delayed = kwargs.pop('delayed', False)

        if is_delayed:
            return cls.async_class(*args, notifier_class=cls, **kwargs)
        else:
            return super().__new__(cls)

    def __init__(self, phone_number):
        self.phone_number = phone_number

    @property
    def client(self):
        return SmsLocMemClient()

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
            'to': self.phone_number,
            'message': self.message,
            'from_': self.sender_name,
        }

        return self.client.sms.send(**smsparams)
