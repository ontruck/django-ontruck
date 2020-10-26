from django_ontruck.notifiers import AsyncNotifier, Notifier
from ..test_app.notifiers import DummySMSNotifier


def test_sms_notifier(mocker):
    notifier = DummySMSNotifier(phone_number='123', delayed=False)
    assert isinstance(notifier, Notifier)

    notifier.send()


def test_sms_async_notifier(mocker):
    notifier = DummySMSNotifier(phone_number='123')
    assert isinstance(notifier, AsyncNotifier)

    notifier.send()
