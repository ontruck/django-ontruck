from unittest.mock import MagicMock, Mock
from django_ontruck.notifiers import (
    AsyncNotifier, MQNotifier, PushNotifier, SegmentNotifier, SlackNotifier, SMSNotifier,
)
from django_ontruck.notifiers.push import Message, Category


class DummyAsyncNotifier(AsyncNotifier):
    @property
    def client(self):
        m = MagicMock()
        m.s.return_value.apply_async.return_value = 'message sent'
        return m


class DummyMQNotifier(MQNotifier):
    async_class = DummyAsyncNotifier

    @property
    def client(self):
        return self.connection_manager

    @property
    def message(self):
        return {'body': 'sample message'}


class DummyMQWithMessageNotifier(MQNotifier):
    async_class = DummyAsyncNotifier

    @property
    def client(self):
        return self.connection_manager

    @property
    def message(self):
        m = Mock()
        m.is_valid.return_value = True
        m.serialize.return_value = {'body': 'sample message'}

        return m


class DummyMQWithInvalidMessageNotifier(MQNotifier):
    async_class = DummyAsyncNotifier

    @property
    def client(self):
        return self.connection_manager

    @property
    def message(self):
        m = Mock()
        m.is_valid.return_value = False

        return m


class DummyMessage(Message):
    @property
    def extra(self):
        return {}


class DummyCategory(Category):
    DUMMY = 'dummy'


class DummyPushNotifier(PushNotifier):
    async_class = DummyAsyncNotifier

    def is_available_for_device_type(self, device_type):
        return True

    def provider_class_for(self, device_type):
        p = MagicMock()
        p.objects.return_value = []
        return p

    @property
    def category(self):
        return DummyCategory.DUMMY

    def message(self, device_type):
        return DummyMessage(device_type=device_type, category=self.category)

    def devices(self, device_type):
        d = MagicMock()
        d.send_message.return_value = None
        return d


class DummySegmentNotifier(SegmentNotifier):
    async_class = DummyAsyncNotifier
    event_id = 'test_event'


class DummySegmentWithIdentityNotifier(SegmentNotifier):
    async_class = DummyAsyncNotifier
    event_id = 'test_event'

    @property
    def identify_properties(self):
        return {'uuid': 123}


class DummySlackNotifier(SlackNotifier):
    async_class = DummyAsyncNotifier

    def __init__(self, model=None):
        super().__init__()

    @property
    def client(self):
        return SlackNotifier.slack_client

    @property
    def channel(self):
        return 'sample-channel'

    @property
    def country_code(self):
        return 'ES'

    @property
    def message(self):
        return 'test message'


class DummySMSNotifier(SMSNotifier):
    async_class = DummyAsyncNotifier

    @property
    def message(self):
        return 'message'

    @property
    def sender_name(self):
        return 'sender'
