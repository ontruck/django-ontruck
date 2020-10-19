import pika


class RabbitMQConnectionManager(object):
    shared_connection = None
    channel_pool = {}

    __slots__ = ('connection_params', )

    def __init__(self, connection_params):
        if not self.shared_connection:
            params = connection_params
            RabbitMQConnectionManager.shared_connection = pika.BlockingConnection(parameters=params)

    def __del__(self):
        for queue, ch in self.channel_pool.items():
            ch.close()

        RabbitMQConnectionManager.channel_pool = {}

        if self.shared_connection and self.shared_connection.is_open:
            self.shared_connection.close()
            RabbitMQConnectionManager.shared_connection = None

    def make_channel(self, queue_name, exchange_name, routing_key):
        ch = self.channel_pool.get(queue_name)

        if not ch:
            channel = self.shared_connection.channel()
            channel.queue_declare(queue_name, durable=True)
            channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)

            self.channel_pool[queue_name] = channel

        return self.channel_pool.get(queue_name)


def rabbitmq_connection_params(user, password, host, **kwargs):
    port = int(kwargs.get('port', 5672))
    heatbeat = int(kwargs.get('heartbeat', 600))
    blocking_connection_timeout = int(kwargs.get('blocking_connection_timeout', 300))
    connection_attempts = int(kwargs.get('connection_attempts', 3))

    credentials = pika.PlainCredentials(user, password)
    pika_params = {
        'host': host,
        'port': port,
        # Set to 0 if no heartbeat want to be checked, but no open connection will be closed in any time
        'heartbeat': heartbeat,
        'blocked_connection_timeout': blocking_connection_timeout,
        'connection_attempts': connection_attempts,
        'credentials': credentials,
    }
    pika_connection_params = pika.ConnectionParameters(**pika_params)
    return pika_connection_params
