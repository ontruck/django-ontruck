from django.db import transaction
import sys
from pytest import fixture, mark, raises
from .test_app.events import FooEvent


class CallbackInvoked(BaseException):
    pass


class TestPytestAtomic:
    @fixture
    def callback(self):
        def throw():
            raise CallbackInvoked()
        return throw

    @mark.django_db
    @mark.run_on_commit_callbacks  # <= This is what's being tested
    def test_it_runs_callbacks_on_the_outermost_test_commit(self, callback):
        atomic = transaction.atomic()

        # Manually invoking __enter__/__exit__ allows us to isolate the commits
        # run on exiting the outer transaction only.
        atomic.__enter__()

        # No on_commit callbacks should be run for the inner transaction
        with transaction.atomic():
            transaction.on_commit(callback)

        transaction.on_commit(callback)

        with raises(CallbackInvoked):
            # Callbacks should be run here and a CallbackInvoked raised
            atomic.__exit__(*sys.exc_info())

    @mark.django_db
    def test_it_does_not_run_callbacks_on_the_outermost_test_commit(self, callback):
        with transaction.atomic():
            # No on_commit callbacks should be run for the inner transaction
            with transaction.atomic():
                transaction.on_commit(callback)

            transaction.on_commit(callback)
        # No callbacks should be run and so no CallbackInvoked raised


    @mark.django_db
    @mark.run_on_commit_callbacks  # <= This is what's being tested
    def test_it_runs_callbacks_from_a_transaction_created_from_on_commit(self, foo_use_case):
        def recursion_handler(attr1, **kwargs):
            from tests.test_app.use_cases import FooUpdateUseCase
            from .test_app.models import FooModel
            uc = FooUpdateUseCase(disable_events=True)
            uc.execute({'instance': FooModel.objects.first(), 'title': attr1})
        # not removing funcs from connection.run_on_commit before execution raises recursion
        FooEvent.connect(recursion_handler)
        foo_use_case.execute({})

