from weakref import WeakKeyDictionary

import django
from django.db import DEFAULT_DB_ALIAS
from django.db.transaction import get_connection, Atomic
from contextlib import ContextDecorator


class WeakKeyDefaultDictionary:
    def __init__(self, default):
        self._store = WeakKeyDictionary()
        self._default = default

    def __getitem__(self, item):
        return self._store.setdefault(item, self._default())

    def __setitem__(self, key, value):
        self._store[key] = value


class DepthTrackingAtomic(ContextDecorator):
    atomic_registry = WeakKeyDefaultDictionary(list)

    def __init__(self, atomic):
        self._atomic = atomic

    @property
    def using(self):
        return self._atomic.using

    @property
    def connection(self):
        return get_connection(using=self.using)

    @property
    def _atomic_stack(self):
        return self.atomic_registry[self.connection]

    def push(self):
        self._atomic_stack.append(self)

    def pop(self):
        self._atomic_stack.pop()

    @property
    def depth(self):
        return len(self._atomic_stack)

    def __enter__(self):
        returned = self._atomic.__enter__()
        self.push()

        return returned

    def __exit__(self, *args):
        returned = self._atomic.__exit__(*args)
        self.pop()

        return returned


class PytestAtomic(DepthTrackingAtomic):
    @property
    def at_test_root_transaction(self):
        return self.depth == 0

    def run_and_clear_commit_hooks(self):
        while self.connection.run_on_commit:
            _, func = self.connection.run_on_commit.pop()
            func()

    def __exit__(self, *args):
        returned = super().__exit__(*args)
        if self.at_test_root_transaction:
            self.run_and_clear_commit_hooks()

        return returned


def pytest_atomic(using=None, savepoint=True, durable=False):
    # Bare decorator: @atomic -- although the first argument is called
    # `using`, it's actually the function being decorated.
    if callable(using):
        return PytestAtomic(Atomic(DEFAULT_DB_ALIAS, savepoint, durable))(using)
    # Decorator: @atomic(...) or context manager: with atomic(...): ...
    else:
        return PytestAtomic(Atomic(using, savepoint, durable))


class PatchedAtomic(ContextDecorator):
    def __init__(self):
        self.original = None

    def __enter__(self):
        self.original = django.db.transaction.atomic
        django.db.transaction.atomic = pytest_atomic

    def __exit__(self, *args):
        django.db.transaction.atomic = self.original
        self.original = None
