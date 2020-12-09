from .test_app.consumers import DummyConsumer, DummyExceptionConsumer


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
