from django_ontruck.notifiers import AsyncNotifier, Notifier
from ..test_app.notifiers import DummyPushNotifier


def test_push_notifier(mocker):
    notifier = DummyPushNotifier(driver_id=1, delayed=False)
    assert isinstance(notifier, Notifier)

    notifier.send()


def test_push_async_notifier(mocker):
    notifier = DummyPushNotifier(driver_id=1)
    assert isinstance(notifier, AsyncNotifier)

    notifier.send()
