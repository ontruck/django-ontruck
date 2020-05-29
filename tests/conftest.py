import pytest

from django.contrib.auth.models import User

from django_ontruck.test import PatchedAtomic
from .test_app.use_cases import FooCreateUseCase
from .test_app.queries import CountFooQuery
from .test_app.events import FooEvent
from .test_app.models import FooModel


@pytest.fixture(autouse=True)
def _run_on_commit_callbacks(request):
    marker = request.node.get_closest_marker("run_on_commit_callbacks")

    if marker:
        with PatchedAtomic():
            yield
    else:
        yield


@pytest.fixture
def foo_use_case():
    return FooCreateUseCase()


@pytest.fixture
def foo_event():
    return FooEvent(attr1='attr1_value')


@pytest.fixture
def user():
    return User.objects.create_user(username='test_user')

@pytest.fixture
def foo_model():
    return FooModel.objects.create(title='title')

@pytest.fixture
def foo_query():
    return CountFooQuery()
