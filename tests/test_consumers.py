import pytest
from .test_app.consumers import DummyConsumer, DummyExceptionConsumer
from django_ontruck.consumer import assure_db_connection
from django.db.utils import InterfaceError
from django.db import connections, DatabaseError


def test_consumer_ack(mocker):
    consumer = DummyConsumer(None)
    body = "{}"
    mock_message = mocker.Mock()

    consumer.handle_message(body, mock_message)

    mock_message.ack.assert_called_once()


def test_consumer_requeue(mocker):
    consumer = DummyExceptionConsumer(None)
    body = "{}"
    mock_message = mocker.Mock()

    consumer.handle_message(body, mock_message)

    mock_message.requeue.assert_called_once()

def test_assure_db(mocker):
    body = "{}"
    mock_message = mocker.Mock()
    conns = [mocker.Mock(), mocker.Mock(), mocker.Mock(), mocker.Mock()]
    conns[0].close_if_unusable_or_obsolete.side_effect = InterfaceError('connection already closed')
    conns[1].close_if_unusable_or_obsolete.side_effect = DatabaseError('pgbouncer cannot connect to server SSL connection has been closed unexpectedly')

    mocker.patch('django.db.connections.all', return_value= conns)
    assure_db_connection(body, mock_message)

    conns[0].close_if_unusable_or_obsolete.assert_called_with()
    conns[1].close_if_unusable_or_obsolete.assert_called_with()
    conns[2].close_if_unusable_or_obsolete.assert_called_with()

    with pytest.raises(DatabaseError) as e_databaseerror:
        conns = [mocker.Mock()]
        conns[0].close_if_unusable_or_obsolete.side_effect = DatabaseError('Not expected error')
        mocker.patch('django.db.connections.all', return_value=conns)
        assure_db_connection(body, mock_message)



