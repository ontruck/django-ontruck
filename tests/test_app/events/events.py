from django.dispatch import Signal

from django_ontruck.events import EventBase


class FooEvent(EventBase):
    signal = Signal(['attr1'])
