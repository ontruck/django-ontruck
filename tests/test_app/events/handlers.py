from django_ontruck.events import receiver
from tests.test_app.events.events import FooEvent


def foo_event_handler(attr1, **kwargs):
    pass


@receiver(FooEvent)
def foo_event_handler_with_receiver(attr1, **kwargs):
    pass
