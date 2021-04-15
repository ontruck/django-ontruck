from abc import ABC, abstractmethod
from customerio import SendEmailRequest

from .notifier import Notifier
from .async_notifier import AsyncNotifier, MetaDelayedNotifier
from .customerio_locmem_client import CustomerIOLocMemClient


class CustomerIONotifier(Notifier, ABC, metaclass=MetaDelayedNotifier):
    __slots__ = ('email_request', )
    async_class = AsyncNotifier

    @classmethod
    def is_default_delayed(cls):
        return True

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        is_delayed = kwargs.pop('delayed', False)
        instance.__init__(*args, **kwargs)

        if is_delayed:
            return cls.async_class(*args, notifier_class=cls, **kwargs)
        else:
            return super().__new__(cls)

    def __init__(self):
        self.email_request = None

    @property
    def request(self) -> SendEmailRequest:
        if self.email_request is None:
            self.email_request = SendEmailRequest(
                to=self.email_to,
                _from=self.email_from,
                subject=self.subject,
                body=self.message,
                identifiers=self.identifiers,
            )

        return self.email_request

    @property
    def client(self):
        return CustomerIOLocMemClient(None)

    @property
    @abstractmethod
    def message(self) -> str:
        return NotImplementedError()

    @property
    @abstractmethod
    def email_to(self) -> str:
        return NotImplementedError()

    @property
    @abstractmethod
    def email_from(self) -> str:
        return NotImplementedError()

    @property
    @abstractmethod
    def subject(self) -> str:
        return NotImplemented

    @property
    def identifiers(self) -> dict:
        return {}

    @property
    def customerio_key(self):
        return None

    def send(self, *args):
        self.client.send_email(self.request)
