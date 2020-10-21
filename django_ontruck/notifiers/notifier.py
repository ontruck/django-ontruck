from abc import ABC, abstractmethod


class Notifier(ABC):
    @classmethod
    def is_default_delayed(cls):
        return False

    @property
    @abstractmethod
    def client(self):
        raise NotImplementedError()

    @abstractmethod
    def send(self, *args):
        raise NotImplementedError()
