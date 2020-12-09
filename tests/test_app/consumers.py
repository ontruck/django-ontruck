from django_ontruck.consumer import ConsumerBase


class DummyConsumer(ConsumerBase):
    @property
    def queue_name(self):
        return 'dummy'

    @property
    def exchange_name(self):
        return 'dummy'

    @property
    def routing_key(self):
        return 'dummy'

    def perform(self, body, message):
        message.ack()


class DummyExceptionConsumer(DummyConsumer):
    def perform(self, body, message):
        raise Exception("Boom!")
