from abc import ABC, abstractmethod
from .device import Device


class Message(ABC):
    __slots__ = ('device_type', 'category', 'message',)

    def __init__(self, device_type, category, message=None):
        self.message = message
        self.device_type = device_type
        self.category = category

    @property
    def title(self):
        return None

    @property
    def body(self):
        return None

    @property
    @abstractmethod
    def extra(self):
        raise NotImplementedError()

    def to_dict(self):
        if self.title and self.body:
            return {'title': self.title, 'body': self.body}
        else:
            d = {'message': self.message, 'extra': self.extra}

            if self.device_type == Device.ANDROID:
                d['use_fcm_notifications'] = False

            return d
