from .device import Device
from .category import Category


class Message(object):
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
    def extra(self):
        if self.device_type == Device.ANDROID:
            return self._android_extra()
        elif self.device_type == Device.IOS:
            return self._ios_extra()
        elif self.device_type == Device.WEB:
            return self._web_extra()
        else:
            raise RuntimeError('invalid device type')

    def to_dict(self):
        if self.title and self.body:
            return {'title': self.title, 'body': self.body}
        else:
            d = {'message': self.message, 'extra': self.extra}

            if self.device_type == Device.ANDROID:
                d['use_fcm_notifications'] = False

            return d

    def _android_extra(self):
        extra = {'priority': 'high', 'category': self.category.value}

        if self.message and 'title' in self.message and 'body' in self.message:
            extra = {**extra, **self.message}

        return extra

    def _ios_extra(self):
        aps = {'category': self.category.value}

        if self.category == Category.PROFILE_UPDATED:
            aps['content-available'] = 1
            return aps

        aps['alert'] = self.message
        aps['sound'] = Category.phone_sound_for(self.category)
        aps['mutable-content'] = 1

        if self.category == Category.OFFER:
            aps['thread-id'] = 'offers-group'

        return {'aps': aps}

    def _web_extra(self):
        extra = {'category': self.category.value}

        if self.message and 'title' in self.message and 'body' in self.message:
            extra = {**extra, **self.message}

        return extra
