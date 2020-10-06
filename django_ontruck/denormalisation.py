from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from importlib import import_module
from re import split
from typing import Callable, Optional, Iterable, Mapping, Type, Sequence
from uuid import uuid4

from django.apps import apps
from django.contrib.contenttypes.models import ContentTypeManager, ContentType
from django.db.models import Model, OneToOneField, CASCADE, prefetch_related_objects
from django.db.models.signals import post_save
from django.dispatch import Signal
from django_ontruck.events import EventBase


def capitalise(string):
    if string == '':
        return ''

    return '{capital}{rest}'.format(
        capital=string[0].capitalize(), rest=string[1:]
    )


def constantise(string):
    return ''.join([capitalise(x) for x in split(r'[\s_]', string)])


class SetAfterInitialisation:
    def __init__(self, instructions):
        self.attribute_name = '_var_{uuid}'.format(uuid=uuid4())
        self.instructions = instructions

    def __set_name__(self, owner, name):
        self.name = name

        setattr(owner, name, self)

    def __get__(self, instance, owner):
        if hasattr(instance, self.attribute_name):
            return getattr(instance, self.attribute_name)

        raise AttributeError(
            f'{self.name} has not been set: {self.instructions}'
        )

    def __set__(self, instance, value):
        setattr(instance, self.attribute_name, value)


skip_denormalisation = object()

missing = object()


def sync_handler(denormaliser, **_kwargs):
    denormaliser()


class Denormalised:
    """
    A descriptor class that is used to control denormalised data.

    ## Example

    class Foo(BaseModel):
        bar = IntegerField(default=0)
        baz = IntegerField(default=3)

        denormalised = Denormalised(
            BaseModel,
            listeners=(
                SignalListener(post_save, sender=Foo),
                EventListener(
                    FooEvent,
                    fields=('my_expensive_prop',)
                )
            ),
            handler=sync_handler
        )

        @denormalised.property(IntegerField())
        def my_expensive_prop(self):
            # Some expensive calculation here

    foo = Foo.objects.last()

    # re-denormalise the denormalised_properties of foo
    Foo.denormalised.denormalise()

    # calculate value of `my_expensive_prop`
    foo.my_expensive_prop

    # Or use the denormalised value
    foo.denormalised.my_expensive_prop
    """
    set_after_initialisation_instructions = 'attach to a model class as a descriptor'

    name = SetAfterInitialisation(set_after_initialisation_instructions)
    model_class = SetAfterInitialisation(set_after_initialisation_instructions)
    parent_model_class = SetAfterInitialisation(set_after_initialisation_instructions)

    def __init__(
        self,
        model_base: Type[Model] = Model,
        listeners: Iterable[Listener] = tuple(),
        field_name: str = 'parent',
        denormalised_model_name: Optional[str] = None,
        related_name: Optional[str] = None,
        handler: Optional[Callable] = None,
    ):
        """

        :param model_base: The base class for the denormalisation model
        :param listeners: Any `Listener` instance used to connect to signals or events
        :param field_name: The name denormalisation model instances will use to refer to their parent instance
        :param denormalised_model_name: the name of the denormalisation model
        :param related_name: The name the parent instance will use to refer to its denormalisation model instance
        :param handler: The handler that will be connected to Denormalise events.
        """
        self.model_base = model_base
        self.denormalised_properties = []
        self.listeners = listeners
        self.field_name = field_name
        self._denormalised_model_name = denormalised_model_name
        self._related_name = related_name

        if handler:
            self.connect(handler)

    def __set_name__(self, owner, name):
        self.name = name
        self.parent_model_class = owner

        factory = DenormalisedModelClassFactory(
            model_base=self.model_base,
            parent_model_class=owner,
            denormalised_properties=self.denormalised_properties,
            parent_related_name=self.related_name,
            parent_field_name=self.field_name,
            model_name=self.denormalised_model_name,
        )

        self.model_class = factory.export()

        post_save.connect(self._post_save_handler, sender=owner)

        self.listen()

        setattr(owner, name, self)

    @property
    def related_name(self):
        return self._related_name or self.default_related_name

    @property
    def default_related_name(self):
        return '_denormalised_{}'.format(self.name)

    @property
    def denormalised_model_name(self):
        return (
            self._denormalised_model_name or self.default_denormalised_model_name
        )

    @property
    def default_denormalised_model_name(self):
        return constantise(
            '{parent_model_name} {name}'.format(
                parent_model_name=self.parent_model_class.__name__,
                name=self.name
            )
        )

    def denormaliser(self, instance, fields):
        if fields is None:
            fields = self.all_fields

        return Denormaliser(
            self.model_class, self.field_name, self.name, instance, fields
        )

    def denormalise(self, instance, fields=None):
        return self.denormaliser(instance, fields)()

    @property
    def all_fields(self):
        return tuple(
            [prop.name for prop in self.model_class.denormalised_properties]
        )

    def __get__(self, instance, owner):
        if not instance:
            return self

        return getattr(instance, self.related_name)

    def property(self, field, prefetches=tuple()):
        def decorator(func):
            denormalised_property = DenormalisedProperty(
                func,
                field=field,
                prefetches=prefetches
            )

            self.denormalised_properties.append(denormalised_property)

            return denormalised_property

        return decorator

    def _post_save_handler(self, instance, created, **_kwargs):
        if created:
            self.model_class.objects.create(
                **{self.field_name: instance}
            )

    def listen(self):
        for listener in self.listeners:
            listener.bind(self)
            listener.connect()

    def connect(self, handler):
        Denormalise.connect(handler, sender=self, weak=False)


class DenormalisedModelClassFactory:
    def __init__(
        self,
        model_base: Type[Model],
        parent_model_class: Type[Model],
        model_name: str,
        denormalised_properties: Iterable[DenormalisedProperty],
        parent_related_name: str,
        parent_field_name: str,
    ):
        self.model_base = model_base
        self.parent_model_class = parent_model_class
        self.model_name = model_name
        self.denormalised_properties = denormalised_properties
        self.parent_related_name = parent_related_name
        self.parent_field_name = parent_field_name

    @property
    def parent_relation(self):
        return OneToOneField(
            self.parent_model_class.__name__,
            on_delete=CASCADE,
            related_name=self.parent_related_name,
        )

    @property
    def fields(self):
        return {
            prop.name: prop.field for prop in
            self.denormalised_properties
        }

    @property
    def attributes(self):
        return {
            '__module__': self.module,
            'denormalised_properties': self.denormalised_properties,
            self.parent_field_name: self.parent_relation,
            **self.fields,
        }

    def build_model_class(self) -> Type[Model]:
        return type(  # noqa
            self.model_name, (self.model_base,), self.attributes
        )

    @property
    def module(self):
        return self.parent_model_class.__module__

    def export(self):
        model_class = self.build_model_class()

        setattr(import_module(self.module), model_class.__name__, model_class)

        return model_class


class Denormalise(EventBase):
    signal = Signal(providing_args=('denormaliser',))

    def send_as_denormalised(self, denormalised: Denormalised):
        self.signal.send(denormalised, **self.data)


class Listener(ABC):
    def __init__(
        self,
        fields=None,
        adapter=lambda instance, **_kwargs: instance,
        denormalise_event=Denormalise,
    ):
        self.fields = fields
        self.adapter = adapter
        self.denormalise_event = denormalise_event

    @abstractmethod
    def connect(self):  # pragma: no cover
        raise NotImplementedError()

    def bind(self, owner):
        self.owner = owner

    owner = SetAfterInitialisation(
        f'set to an instance of `{Denormalised.__name__}` using the `{bind.__name__}` method'
    )

    def handle(self, *args, **kwargs):
        instance = self.adapter(*args, **kwargs)

        if instance is skip_denormalisation:
            return

        self.denormalise_event(
            denormaliser=self.owner.denormaliser(instance, self.fields),
        ).send_as_denormalised(denormalised=self.owner)


class SignalListener(Listener):
    def __init__(self, signal, sender, *args, **kwargs):
        self.signal = signal
        self.sender = sender

        super().__init__(*args, **kwargs)

    def connect(self):
        self.signal.connect(
            self.handle,
            sender=self.sender,
            weak=False,
        )


class EventListener(SignalListener):
    def __init__(self, event, *args, **kwargs):
        self.event = event

        super().__init__(event.signal, sender=self.event.sender, *args, **kwargs)


class DenormalisedProperty(property):
    def __init__(self, fget, field, prefetches):
        self.name = fget.__name__
        self.field = field
        self.prefetches = prefetches

        super().__init__(fget=fget)


@dataclass
class Denormaliser:
    """
    Given an instance of a denormalisation model class, creates or
    updates an instance of the denormalisation model_class class.
    """

    model_class: Type[Model]
    parent_field_name: str
    denormalised_attr: str
    instance: Model
    fields: Sequence[str]
    prefetch_related_objects_: Callable = field(
        default=prefetch_related_objects,
        compare=False,
        repr=False
    )

    @property
    def prefetches(self):
        return sum(
            [
                prop.prefetches
                for prop in self.model_class.denormalised_properties
                if prop.name in self.fields
            ],
            tuple()
        )

    @property
    def model(self) -> Type[Model]:
        return self.instance.__class__

    def __call__(self, refresh_after_update=True):
        self.prefetch_related_objects_([self.instance], *self.prefetches)

        self.model_class.objects.update_or_create(
            **{self.parent_field_name: self.instance},
            defaults={
                field: getattr(self.instance, field) for field in self.fields
            }
        )

        if refresh_after_update:
            self.instance.refresh_from_db()


class SerialiseDenormaliser:
    def __init__(
        self,
        content_type_repo: ContentTypeManager = ContentType.objects,
    ):
        self.content_type_repo = content_type_repo

    def __call__(self, denormaliser: Denormaliser) -> Mapping:
        content_type = self.content_type_repo.get_for_model(denormaliser.model)

        return {
            'app_label': content_type.app_label,
            'model_name': content_type.model,
            'denormalised_attr': denormaliser.denormalised_attr,
            'instance_id': denormaliser.instance.id,
            'fields': list(denormaliser.fields)
        }


serialise_denormaliser = SerialiseDenormaliser()


class DeserialiseDenormaliser:
    def __init__(self, get_model=apps.get_model):
        self.get_model = get_model

    def __call__(self, denormaliser_data: Mapping) -> Denormaliser:
        model = self.get_model(
            denormaliser_data['app_label'],
            denormaliser_data['model_name']
        )

        denormalised = getattr(model, denormaliser_data['denormalised_attr'])

        instance = model.objects.get(id=denormaliser_data['instance_id'])

        denormaliser = denormalised.denormaliser(
            instance, denormaliser_data['fields']
        )

        return denormaliser


deserialise_denormaliser = DeserialiseDenormaliser()
