from __future__ import annotations
from .result import Result

from typing import Any, Callable, TypeVar, Optional, final


T = TypeVar('T')
U = TypeVar('U')

E = TypeVar('E')
F = TypeVar('F')


@final
class Error(Result[Any, E]):
    _inner_value: E

    def __init__(self, error: E):
        self._inner_value = error

    def is_ok(self) -> bool:
        return False

    def is_error(self) -> bool:
        return True

    def and_then(self, fn: Callable[[T], Result[T, E]]) -> Result[T, E]:
        return self

    def or_else(self, fn: Callable[[E], Result[T, E]]) -> Result[T, E]:
        return fn(self._inner_value)

    def unwrap_or(self, default: T) -> T:
        return default

    def unwrap_or_else(self, fn: Callable[[E], E]) -> E:
        return fn(self._inner_value)

    def map(self, fn: Callable[[T], Result[U, E]]) -> Result[T, E]:
        return self

    def map_or(
        self, fn: Callable[[T], T], default: Optional[T] = None
    ) -> Optional[T]:
        return default

    def map_or_else(
        self, fn: Callable[[T], U], defaultfn: Callable[[E], U]
    ) -> U:
        return defaultfn(self._inner_value)

    def map_err(self, fn: Callable[[E], Result[T, F]]) -> Result[T, F]:
        return fn(self._inner_value)

    def unwrap(self) -> E:
        return self._inner_value
