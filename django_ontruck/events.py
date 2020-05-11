from django.dispatch.dispatcher import receiver as django_receiver


class EventBase:
    sender = None
    signal = None

    def __init__(self, **kwargs):
        self.data = kwargs

    def send(self):
        self.signal.send(self.sender, **self.data)

    @classmethod
    def connect(cls, receiver, sender=None, weak=True, dispatch_uid=None):
        cls.signal.connect(receiver, sender, weak, dispatch_uid)

    @classmethod
    def disconnect(cls, receiver=None, sender=None, dispatch_uid=None):
        cls.signal.disconnect(receiver, sender, dispatch_uid)


def receiver(event, **kwargs):
    return django_receiver(event.signal, **kwargs)
