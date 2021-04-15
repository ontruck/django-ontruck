from django_ontruck.notifiers import AsyncNotifier, Notifier
from ..test_app.notifiers import DummyCustomerIONotifier


def test_customerio_notifier(mocker):
    notifier = DummyCustomerIONotifier(delayed=False)
    assert isinstance(notifier, Notifier)

    notifier.send()


def test_customerio_async_notifier(mocker):
    notifier = DummyCustomerIONotifier()
    assert isinstance(notifier, AsyncNotifier)

    notifier.send()
