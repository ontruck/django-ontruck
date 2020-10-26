import json
from abc import ABC, abstractmethod

from .push.device import Device
from .async_notifier import AsyncNotifier, MetaDelayedNotifier
from .notifier import Notifier


class PushNotifier(Notifier, ABC, metaclass=MetaDelayedNotifier):
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

    @property
    def client(self):
        return None  # clients are managed by device providers

    @property
    @abstractmethod
    def category(self):
        raise NotImplementedError()

    @abstractmethod
    def message(self, device_type):
        raise NotImplementedError()

    @abstractmethod
    def is_available_for_device_type(self, device_type):
        raise NotImplementedError()

    @abstractmethod
    def provider_class_for(self, device_type):
        raise NotImplementedError()

    @abstractmethod
    def devices(self, device_provicer):
        raise NotImplementedError()

    def send(self):
        device_types = [device_type for _, device_type in Device.__members__.items() if
                        self.is_available_for_device_type(device_type)]
        for device_type in device_types:
            msg = self.message(device_type)

            device_provider = self.provider_class_for(device_type)
            devices = self.devices(device_provider)

            if device_type == Device.WEB:
                web_json = json.dumps(msg.to_dict())
                for device in devices:
                    self.send_web_device(device, web_json)
            else:
                devices.send_message(**msg.to_dict())

    def send_web_device(self, device, web_json):
        device.send_message(web_json)
