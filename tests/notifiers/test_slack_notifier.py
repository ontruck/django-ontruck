from django_ontruck.notifiers import AsyncNotifier, Notifier
from ..test_app.notifiers import DummySlackNotifier


def test_slack_notifier(mocker):
    notifier = DummySlackNotifier(delayed=False)
    assert isinstance(notifier, Notifier)

    notifier.send()


def test_slack_async_notifier(mocker):
    notifier = DummySlackNotifier()
    assert isinstance(notifier, AsyncNotifier)

    notifier.send()
