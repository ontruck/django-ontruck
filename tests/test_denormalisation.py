from json import dumps
from unittest.mock import create_autospec

from django.db.models import Model, prefetch_related_objects
from pytest import fixture, mark, raises

from django_ontruck.denormalisation import constantise, Denormaliser, Denormalise, serialise_denormaliser, \
    deserialise_denormaliser, skip_denormalisation, Denormalised, EventListener
from django_ontruck.models import BaseModel
from tests.test_app.events.events import BarEvent, baz
from tests.test_app.models import DenormalisedModel, FooModel, DefaultDenormalisedModel


class TestDenormalisation:
    class TestCamelCase:
        @mark.parametrize(
            ('string', 'expected'),
            (
                ('snake_case', 'SnakeCase'),
                ('CamelCase', 'CamelCase'),
                ('with spaces', 'WithSpaces'),
                ('', ''),
                (' _ ', '')
            )
        )
        def test_camel_case(self, string, expected):
            assert constantise(string) == expected

    class TestDenormalised:
        @fixture
        def instance(self):
            return DenormalisedModel.objects.create()

        @mark.django_db
        def test_model_base(self, instance):
            assert isinstance(instance.calculated_fields, BaseModel)

        @mark.django_db
        def test_field_name(self, instance):
            assert instance.calculated_fields.denormalised_model == instance

        @mark.django_db
        def test_denormalised_model_name(self, instance):
            assert (
                instance.calculated_fields.__class__.__name__ ==
                'DenormalisedCalculatedFields'
            )

        @mark.django_db
        def test_related_name(self, instance):
            assert (
                instance._calculated_fields is instance.calculated_fields
            )

        @mark.django_db
        def test_it_has_an_associated_calculated_fields_model(self, instance):
            assert instance.calculated_fields

            assert not instance.calculated_fields.bar
            assert not instance.calculated_fields.baz

        @mark.django_db
        def test_we_can_access_the_properties_directly(self, instance):
            assert instance.bar == 'bar'
            assert instance.baz == 'baz'

        @mark.django_db
        def test_we_can_denormalise_the_values_and_access_them(self, instance):
            DenormalisedModel.calculated_fields.denormalise(instance)

            assert instance.calculated_fields.bar == 'bar'
            assert instance.calculated_fields.baz == 'baz'

        def test_it_listens_to_denormalise_events(self):
            assert Denormalise.signal.has_listeners(
                sender=DenormalisedModel.calculated_fields
            )

        @mark.django_db
        def test_sync_event_connectors_denormalise_synchronously(
            self, instance
        ):
            BarEvent(instance=instance).send()

            assert instance.calculated_fields.bar == 'bar'

            assert not instance.calculated_fields.baz

        @mark.django_db
        def test_signal_connectors_denormalise_synchronously(
            self, instance
        ):
            baz.send(sender=FooModel, instance=instance)

            assert instance.calculated_fields.baz == 'baz'

            assert not instance.calculated_fields.bar

        class TestDefaultValues:
            @fixture
            def instance(self):
                return DefaultDenormalisedModel.objects.create()

            @mark.django_db
            def test_model_base(self, instance):
                assert isinstance(instance.calculated_fields, Model)

            @mark.django_db
            def test_listeners(self, instance):
                assert (
                    DefaultDenormalisedModel.calculated_fields.listeners ==
                    tuple()
                )

            @mark.django_db
            def test_field_name(self, instance):
                assert instance.calculated_fields.parent == instance

            @mark.django_db
            def test_denormalised_model_name(self, instance):
                assert (
                    instance.calculated_fields.__class__.__name__ ==
                    'DefaultDenormalisedModelCalculatedFields'
                )

            @mark.django_db
            def test_related_name(self, instance):
                assert (
                    instance._denormalised_calculated_fields is
                    instance.calculated_fields
                )

            def test_it_does_not_listen_to_denormalise_events(self):
                assert not Denormalise.signal.has_listeners(
                    sender=DefaultDenormalisedModel.calculated_fields
                )

    class TestSerialisation:
        @fixture
        def instance(self):
            return DenormalisedModel.objects.create()

        @fixture
        def model_class(self):
            return DenormalisedModel.calculated_fields.model_class

        @fixture
        def parent_field_name(self):
            return 'denormalised_model'

        @fixture
        def denormalised_attr(self):
            return 'calculated_fields'

        @fixture
        def fields(self):
            return ['bar', 'baz']

        @fixture
        def prefetch_related_objects_(self):
            return create_autospec(prefetch_related_objects)

        @fixture
        def denormaliser(
            self, model_class, parent_field_name,
            denormalised_attr, instance, fields, prefetch_related_objects_
        ):
            return Denormaliser(
                model_class=model_class,
                parent_field_name=parent_field_name,
                denormalised_attr=denormalised_attr,
                instance=instance,
                fields=fields,
                prefetch_related_objects_=prefetch_related_objects_
            )

        @mark.django_db
        def test_it_serialises_to_json_serialisable_data(self, denormaliser):
            assert dumps(serialise_denormaliser(denormaliser))

        @mark.django_db
        def test_it_deserialises_serialised_data_to_an_identical_denormaliser(
            self, denormaliser
        ):
            serialised = serialise_denormaliser(denormaliser)
            deserialised = deserialise_denormaliser(serialised)

            assert deserialised == denormaliser

    class TestListener:
        @fixture
        def mock_denormalise_event(self):
            return create_autospec(Denormalise, instance=False)

        @fixture
        def test_listener(self, mock_denormalise_event):
            return EventListener(
                BarEvent, denormalise_event=mock_denormalise_event
            )

        def test_denormalise_event_is_not_sent_when_the_adapter_returns_skip(
            self, test_listener, mock_denormalise_event
        ):
            test_listener.handle(instance=skip_denormalisation)

            assert not mock_denormalise_event.called

    class TestAttributesSetAfterInitialisation:
        @fixture
        def denormalised(self):
            return Denormalised()

        @mark.parametrize(
            ('attr',),
            (
                ('name',),
                ('model',),
                ('paren_model_class',),
            )
        )
        def test_attributes_set_on_initialisation(self, attr, denormalised):
            with raises(AttributeError):
                getattr(denormalised, attr)

        @fixture
        def listener(self):
            return EventListener(BarEvent)

        def test_owner(self, listener):
            with raises(AttributeError):
                _ = listener.owner
