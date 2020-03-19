
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
