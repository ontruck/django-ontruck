from django.apps import AppConfig


class TestAppConfig(AppConfig):
    name = 'tests.test_app'

    def ready(self):
        from .events import FooEvent, foo_event_handler
        FooEvent.connect(foo_event_handler)
