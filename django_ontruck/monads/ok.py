from __future__ import annotations
from .result import Result

from typing import Any, Callable, Optional, TypeVar, final


T = TypeVar('T')
U = TypeVar('U')

E = TypeVar('E')
F = TypeVar('F')


@final
class Ok(Result[T, Any]):
    _inner_value: T

    def __init__(self, value: T):
        self._inner_value = value

    def is_ok(self) -> bool:
        return True

    def is_error(self) -> bool:
        return False

    def and_then(self, fn: Callable[[T], Result[T, E]]) -> Result[T, E]:
        return fn(self._inner_value)

    def or_else(self, fn: Callable[[T], Result[T, E]]) -> Result[T, E]:
        return self

    def unwrap_or(self, default: T) -> T:
        return self._inner_value

    def unwrap_or_else(self, fn: Callable[[T], T]) -> T:
        return self._inner_value

    def map(self, fn: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return fn(self._inner_value)

    def map_or(
        self, fn: Callable[[T], T], default: Optional[T] = None
    ) -> Optional[T]:
        return fn(self._inner_value)

    def map_or_else(
        self, fn: Callable[[T], U], defaultfn: Callable[[T], U]
    ) -> U:
        return fn(self._inner_value)

    def map_err(self, fn: Callable[[T], T]) -> Result[T, E]:
        return self

    def unwrap(self) -> T:
        return self._inner_value
