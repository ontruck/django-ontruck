import pytest
from unittest.mock import MagicMock
from django_ontruck.notifiers import AsyncNotifier, Notifier
from ..test_app.notifiers import DummySegmentNotifier, DummySegmentWithIdentityNotifier


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.uuid = 'uuid'
    return user


def test_segment_notifier(mocker, mock_user):
    notifier = DummySegmentNotifier(user=mock_user, delayed=False)
    assert isinstance(notifier, Notifier)

    notifier.send()


def test_segment_async_notifier(mocker, mock_user):
    notifier = DummySegmentNotifier(user=mock_user)
    assert isinstance(notifier, AsyncNotifier)

    notifier.send()


def test_segment_with_identity_notifier(mocker, mock_user):
    notifier = DummySegmentWithIdentityNotifier(user=mock_user, delayed=False)
    assert isinstance(notifier, Notifier)

    notifier.send()
