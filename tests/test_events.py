from django.db import transaction

from django_ontruck.use_cases import UseCaseBase
from django_ontruck.events import EventBase

from .test_app.events import FooEvent, foo_event_handler


class TestEvents:

    def test_event_creation(self, foo_event):
        assert foo_event.data == {'attr1': 'attr1_value'}

    def test_event_send(self, mocker, foo_event):
        mock_signal_send = mocker.patch('django.dispatch.Signal.send')
        foo_event.send()
        mock_signal_send.called_once_with(attr1='attr1_value')

    def test_connect(self, mocker, foo_event):
        mock_event_handler = mocker.patch('tests.test_app.events.handlers.foo_event_handler')
        foo_event.send()
        mock_event_handler.called_once_with(attr1='attr1_value')
