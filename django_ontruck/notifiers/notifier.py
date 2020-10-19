from abc import ABC, abstractmethod


class Notifier(ABC):
    @classmethod
    def is_default_delayed(cls):
        return False

    @abstractmethod
    def send(self, *args):
        raise NotImplementedError()
