import pytest
from datetime import datetime, timedelta

from django.contrib.contenttypes.models import ContentType
from django_ontruck.notifiers.async_notifier import load_class, to_primitives, from_primitives, AsyncNotifier
from ..test_app.notifiers import DummySlackNotifier


@pytest.fixture
def foo_model_content_type_id(foo_model):
    return ContentType.objects.get_for_model(foo_model).id


@pytest.fixture
def bar_model_content_type_id(bar_model):
    return ContentType.objects.get_for_model(bar_model).id


@pytest.fixture
def foobar_model_content_type_id(foobar_model):
    return ContentType.objects.get_for_model(foobar_model).id


@pytest.fixture
def ct_fixtures(foo_model_content_type_id, bar_model_content_type_id, foobar_model_content_type_id):
    return {
        'foo_model': foo_model_content_type_id,
        'bar_model': bar_model_content_type_id,
        'foobar_model': foobar_model_content_type_id,
    }


@pytest.mark.parametrize('class_path, expected', [
    ('django_ontruck.notifiers.async_notifier.AsyncNotifier', AsyncNotifier),
    ('django_ontruck.notifiers.not_exists', None),
])
def test_load_class(class_path, expected):
    cls = load_class(class_path)

    assert cls is expected


def test_to_primitives_with_primitive_data():
    input_args, input_kwargs = (
        (1, 'sample'),
        {'key1': 1, 'key2': 'foo'},
    )
    expected_args, expected_kwargs = (
        (1, 'sample'),
        {'key1': 1, 'key2': 'foo', 'primitive_indexes': {}, 'primitive_keys': {}},
    )

    output_args, output_kwargs = to_primitives(*input_args, **input_kwargs)

    assert output_args == expected_args
    assert output_kwargs == expected_kwargs


@pytest.mark.django_db
def test_to_primitives_with_model_data(ct_fixtures, foo_model, bar_model, foobar_model):
    input_args, input_kwargs = (
        (foo_model, bar_model),
        {'key1': 1, 'key2': foobar_model},
    )
    output_args, output_kwargs = to_primitives(*input_args, **input_kwargs)

    expected_args, expected_kwargs = (
        (foo_model.id, bar_model.id),
        {'key1': 1, 'key2': foobar_model.id,
         'primitive_keys': {'key2': ct_fixtures['foobar_model']},
         'primitive_indexes': {0: ct_fixtures['foo_model'], 1: ct_fixtures['bar_model']}}
    )

    assert output_args == expected_args
    assert output_kwargs == expected_kwargs


def test_from_primitives_with_primitive_data():
    input_args, input_kwargs = (
        (1, 'sample'),
        {'key1': 1, 'key2': 'foo', 'primitive_indexes': {}, 'primitive_keys': {}},
    )
    expected_args, expected_kwargs = (
        (1, 'sample'),
        {'key1': 1, 'key2': 'foo'},
    )

    output_args, output_kwargs = from_primitives(*input_args, **input_kwargs)

    assert output_args == expected_args
    assert output_kwargs == expected_kwargs


@pytest.mark.django_db
def test_from_primitives_with_model_data(ct_fixtures, foo_model, bar_model, foobar_model):
    input_args, input_kwargs = (
        (foo_model.id, bar_model.id),
        {'key1': 1, 'key2': foobar_model.id,
         'primitive_keys': {'key2': ct_fixtures['foobar_model']},
         'primitive_indexes': {0: ct_fixtures['foo_model'], 1: ct_fixtures['bar_model']}}
    )
    expected_args, expected_kwargs = (
        (foo_model, bar_model),
        {'key1': 1, 'key2': foobar_model},
    )

    output_args, output_kwargs = from_primitives(*input_args, **input_kwargs)

    assert output_args == expected_args
    assert output_kwargs == expected_kwargs


@pytest.mark.django_db
def test_idempotence(foo_model, bar_model, foobar_model):
    input_args, input_kwargs = (
        (foo_model, bar_model),
        {'key1': 1, 'key2': foobar_model},
    )

    aux_args, aux_kwargs = to_primitives(*input_args, **input_kwargs)
    expected_args, expected_kwargs = from_primitives(*aux_args, **aux_kwargs)

    assert input_args == expected_args
    assert input_kwargs == expected_kwargs


@pytest.mark.django_db
def test_async_notifier(foo_model):
    async_notifier = DummySlackNotifier(foo_model, delayed=True)
    mock_client = async_notifier.client
    assert isinstance(async_notifier, AsyncNotifier)
    async_notifier.send()

    mock_client.called_with(
        notifier_class=DummySlackNotifier.__class__,
        foo_model_id=foo_model.id,
        primitive_keys=['foo_model_id'],
    )


@pytest.mark.django_db
@pytest.mark.parametrize('celery_opts, expected_key', [
    ({'eta': datetime.now() + timedelta(minutes=5)}, 'eta'),
    ({'countdown': 60}, 'countdown')
])
def test_async_notifier_with_celery_opts(foo_model, celery_opts, expected_key):
    async_notifier = DummySlackNotifier(foo_model, delayed=True, **celery_opts)
    mock_client = async_notifier.client
    assert isinstance(async_notifier, AsyncNotifier)
    async_notifier.send()

    mock_client.called_with(
        notifier_class=DummySlackNotifier.__class__,
        foo_model_id=foo_model.id,
        primitive_keys=['foo_model_id'],
    )
