from django.dispatch import Signal

from django_ontruck.events import EventBase


class FooEvent(EventBase):
    signal = Signal(['attr1'])


class BarEvent(EventBase):
    signal = Signal(['instance'])


baz = Signal(['instance'])
