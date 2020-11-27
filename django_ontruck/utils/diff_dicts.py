from __future__ import annotations

from abc import ABC, abstractmethod
from collections import OrderedDict, Sequence, Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Hashable, Iterable


class Missing:
    def __str__(self):
        return ''


missing = Missing()


class Diff(ABC):
    @abstractmethod
    def __iter__(self):  # pragma: no cover
        raise NotImplementedError()

    @property
    @abstractmethod
    def left(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def right(self):
        raise NotImplementedError()


class Symbol(Enum):
    Modification = '*'
    Addition = '+'
    Deletion = '-'


@dataclass
class KeyPath:
    keys: Iterable[Hashable]

    def __init__(self, *keys):
        self.keys = keys

    def __str__(self):
        return f'/{"/".join(str(key) for key in self.keys)}'

    def __iter__(self):
        yield from self.keys


class ScalarDiff(Diff, ABC):
    def __init__(self, left: object, right: object, symbol: Symbol):
        self._left = left
        self._right = right
        self.symbol = symbol

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right

    def __iter__(self):
        yield KeyPath(), self

    def __eq__(self, other):
        return (self.left, self.right) == (other.left, other.right)

    def __hash__(self):
        return hash((self.left, self.right))

    @property
    def description(self):
        return f'left: {self.left} | right: {self.right}'


class Modification(ScalarDiff):
    def __init__(self, left: object, right: object):
        super().__init__(left, right, Symbol.Modification)


class Addition(ScalarDiff):
    def __init__(self, right: object):
        super().__init__(missing, right, Symbol.Addition)


class Deletion(ScalarDiff):
    def __init__(self, left: object):
        super().__init__(left, missing, Symbol.Deletion)


@dataclass(frozen=True)
class DictDiff(Diff):
    items: OrderedDict[Hashable, Diff]

    @classmethod
    def empty(cls):
        return cls(OrderedDict())

    def __iter__(self):
        for key, values in self.items.items():
            yield from ((KeyPath(key, *value[0]), value[1]) for value in values)

    def __getitem__(self, item):
        return self.items[item]

    def __len__(self):
        return len(tuple(iter(self)))

    def __str__(self):
        return '\n'.join(
            f"[ {diff.symbol.value} ] {key} : {diff.description}"
            for key, diff in self
        )

    def _partition(self, side):
        return OrderedDict(
            [
                (key, getattr(diff, side)) for key, diff in self.items.items()
            ]
        )

    @property
    def left(self):
        return self._partition('left')

    @property
    def right(self):
        return self._partition('right')

    __repr__ = __str__


def is_scalar(value):
    if isinstance(value, Mapping):
        return False

    elif not isinstance(value, Sequence):
        return True

    try:
        return value[0][0] == value[0]
    except (TypeError, IndexError):
        return False


class Comparison:
    def __init__(self, key: Hashable, left: object, right: object):
        self.key = key
        self.left = left
        self.right = right

    @property
    def differs(self):
        return self.left != self.right

    @property
    def addition(self):
        return self.left is missing

    @property
    def deletion(self):
        return self.right is missing

    @property
    def scalar(self):
        return is_scalar(self.left) or is_scalar(self.right)


class Builder(ABC):
    @abstractmethod
    def build(self) -> Diff:  # pragma: no cover
        pass


class ScalarBuilder(Builder):
    def __init__(self, scalar):
        self.scalar = scalar

    def build(self) -> ScalarDiff:
        return self.scalar


class DictDiffBuilder(Builder):
    def __init__(self):
        self.items: OrderedDict[Hashable, Builder] = OrderedDict()

    def __setitem__(self, key, value):
        self.items[key] = value

    def build(self) -> DictDiff:
        return DictDiff(
            OrderedDict(
                [(key, value.build()) for key, value in self.items.items()]
            )
        )


def adapt_to_mapping(mapping_or_sequence):
    if isinstance(mapping_or_sequence, Mapping):
        return mapping_or_sequence

    return {index: item for index, item in enumerate(mapping_or_sequence)}


class DiffDicts:
    def __init__(self, sort_method):
        self.sort_method = sort_method
        self._queue = []

    def _comparisons(self):
        while True:
            if self._queue:
                yield self._queue.pop(0)
            else:
                return

    def _enqueue(self, left, right, builder):
        left, right = adapt_to_mapping(left), adapt_to_mapping(right)

        self._queue.extend(
            [
                (comparison, builder)
                for key in self.sort_method(set(left) | set(right))
                if (
                    comparison := Comparison(
                        key, left.get(key, missing), right.get(key, missing)
                    )
                ).differs
            ]
        )

    def _handle_comparison(self, comparison, builder):
        if comparison.addition:
            builder[comparison.key] = ScalarBuilder(Addition(comparison.right))

        elif comparison.deletion:
            builder[comparison.key] = ScalarBuilder(Deletion(comparison.left))

        elif comparison.scalar:
            diff = Modification(comparison.left, comparison.right)

            builder[comparison.key] = ScalarBuilder(diff)

        else:
            builder[comparison.key] = next_builder = DictDiffBuilder()

            self._enqueue(comparison.left, comparison.right, next_builder)

    def __call__(self, left, right):
        try:
            builder = DictDiffBuilder()

            self._enqueue(left, right, builder)

            for comparison, current_builder in self._comparisons():
                self._handle_comparison(comparison, current_builder)

            return builder.build()

        finally:
            self._queue = []


def diff_dicts(left, right, sort_method=sorted):
    return DiffDicts(sort_method)(left, right)
