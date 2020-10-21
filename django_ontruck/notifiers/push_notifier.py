import json
import logging
from abc import ABC, abstractmethod

from push_notifications.webpush import WebPushError

from .push.device import Device
from .async_notifier import AsyncNotifier, MetaDelayedNotifier
from .notifier import Notifier


logger = logging.getLogger(__name__)


class PushNotifier(Notifier, ABC, metaclass=MetaDelayedNotifier):
    __slots__ = ('driver_id',)

    @classmethod
    def is_default_delayed(cls):
        return True

    def __new__(cls, *args, **kwargs):
        is_delayed = kwargs.pop('delayed', False)

        if is_delayed:
            return AsyncNotifier(*args, notifier_class=cls, **kwargs)
        else:
            return super().__new__(cls)

    def __init__(self, driver_id):
        self.driver_id = driver_id

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
        raise NotImplementedError

    @abstractmethod
    def provider_class_for(self, device_type):
        raise NotImplementedError

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
                    try:
                        device.send_message(web_json)
                    except WebPushError as e:
                        result = str(e)
                        if any(code in result for code in ['404', '410']):
                            # remove device from db
                            device.delete()
                        else:
                            logger.error(e)
            else:
                devices.send_message(**msg.to_dict())

    def devices(self, device_provider):
        return device_provider.objects.filter(user__driver_id=self.driver_id)
