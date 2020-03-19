
from django.dispatch import Signal
from django.db import transaction

from pytest import fixture, mark

from .test_app.use_cases import FooUseCase


class TestUseCases:

    @mark.django_db
    def test_use_case_in_commit(self, foo_use_case):
        foo_use_case.execute({})
        assert len(foo_use_case.events) == 1
        assert foo_use_case.events[0].data == {'attr1': 'attr1_value'}

    @mark.django_db
    @mark.run_on_commit_callbacks
    def test_use_case_post_commit(self, mocker, foo_use_case):
        mock_event_send = mocker.patch('django_ontruck.events.EventBase.send')
        foo_use_case.execute({})
        mock_event_send.assert_called_once_with()

    @mark.django_db
    @mark.run_on_commit_callbacks
    def test_use_case_post_commit_events_disabled(self, mocker, foo_use_case):
        mock_event_send = mocker.patch('django_ontruck.events.EventBase.send')
        foo_use_case.disable_events = True
        foo_use_case.execute({})
        mock_event_send.assert_not_called()
