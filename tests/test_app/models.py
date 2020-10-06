from django.db import models
from django.db.models import Model

from django_ontruck.denormalisation import (
    Denormalised, SignalListener, EventListener, sync_handler
)
from django_ontruck.models import BaseModel
from tests.test_app.events.events import BarEvent, baz


class FooModel(BaseModel):
    title = models.CharField(max_length=50)
    extra = models.CharField(max_length=50, blank=True)
    pre_serializer = models.CharField(max_length=50, blank=True, null=True)


class BarModel(BaseModel):
    name = models.CharField(max_length=50)


class FoobarModel(BaseModel):
    quantity = models.IntegerField()


def lookup_denormalised_model_by_id(instance_id, **_kwargs):
    return DenormalisedModel.objects.get(id=instance_id)


class DenormalisedModel(BaseModel):
    calculated_fields = Denormalised(
        BaseModel,
        listeners=(
            EventListener(
                BarEvent,
                fields=('bar',)
            ),
            SignalListener(
                baz,
                sender=FooModel,
                fields=('baz',),
            )
        ),
        field_name='denormalised_model',
        denormalised_model_name='DenormalisedCalculatedFields',
        related_name='_calculated_fields',
        handler=sync_handler
    )

    @calculated_fields.property(
        models.CharField(max_length=100)
    )
    def bar(self):
        return 'bar'

    @calculated_fields.property(
        models.CharField(max_length=100)
    )
    def baz(self):
        return 'baz'


class DefaultDenormalisedModel(BaseModel):
    calculated_fields = Denormalised()
