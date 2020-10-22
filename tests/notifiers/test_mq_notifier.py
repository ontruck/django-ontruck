from django_ontruck.notifiers import AsyncNotifier, Notifier
from ..test_app.notifiers import DummyMQNotifier, DummyMQWithMessageNotifier, DummyMQWithInvalidMessageNotifier


def test_mq_notifier(mocker):
    notifier = DummyMQNotifier(queue_name='test', delayed=False)
    assert isinstance(notifier, Notifier)

    notifier.send()


def test_mq_async_notifier(mocker):
    notifier = DummyMQNotifier(queue_name='test')
    assert isinstance(notifier, AsyncNotifier)

    notifier.send()


def test_mq_with_message_notifier(mocker):
    notifier = DummyMQWithMessageNotifier(queue_name='test', delayed=False)
    assert isinstance(notifier, Notifier)

    notifier.send()


def test_mq_with_invalid_message_notifier(mocker):
    notifier = DummyMQWithInvalidMessageNotifier(queue_name='test', delayed=False)
    assert isinstance(notifier, Notifier)

    notifier.send()
