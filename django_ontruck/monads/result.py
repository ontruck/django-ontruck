from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Callable, Optional, TypeVar, Generic, Union


ValueType = TypeVar('ValueType')
U = TypeVar('U')  # generic type for values

ErrorType = TypeVar('ErrorType')
F = TypeVar('F')  # generic type for errors


class Result(Generic[ValueType, ErrorType], metaclass=ABCMeta):
    """Result monad interface.
    """
    _inner_value: Union[ValueType, ErrorType]

    @abstractmethod
    def is_ok(self) -> bool:
        """Returns True if `self` is an `Ok`
        """
        return NotImplemented

    @abstractmethod
    def is_error(self) -> bool:
        """Returns True if `self` is an `Error`
        """
        return NotImplemented

    @abstractmethod
    def and_then(
        self, fn: Callable[[ValueType], Result[ValueType, ErrorType]]
    ) -> Result[ValueType, ErrorType]:
        """Calls `fn` if the result is `Ok`, otherwise returns the `Error`
           value of `self`.
        """
        return NotImplemented

    @abstractmethod
    def or_else(
        self, fn: Callable[[ValueType], Result[ValueType, ErrorType]]
    ) -> Result[ValueType, ErrorType]:
        """Calls `fn` if the result is `Error`, otherwise returns the `Ok`
           value of `self`
        """
        return NotImplemented

    @abstractmethod
    def unwrap_or(self, default: ValueType) -> ValueType:
        """Returns a contained `Ok` value or a provided default.
        """
        return NotImplemented

    @abstractmethod
    def unwrap_or_else(
        self, fn: Callable[[ValueType], ValueType]
    ) -> ValueType:
        """Return the contained `Ok` value or computes it from a closure.
        """
        return NotImplemented

    @abstractmethod
    def map(
        self, fn: Callable[[ValueType], Result[U, ErrorType]]
    ) -> Union[Result[ValueType, ErrorType], Result[U, ErrorType]]:
        """Maps Result(T, E) to Result(U, E) by applying a function to a
           contained `Ok` value, leaving an `Error` value untouched.
        """
        return NotImplemented

    @abstractmethod
    def map_or(
        self,
        fn: Callable[[ValueType], ValueType],
        default: Optional[ValueType] = None
    ) -> Optional[ValueType]:
        """Applies a function to the contained value if `Ok`, or return the
           provided default if `Error`
        """
        return NotImplemented

    @abstractmethod
    def map_or_else(
        self, fn: Callable[[ValueType], U], defaultfn: Callable[[ValueType], U]
    ) -> U:
        """Maps a Result(T, E) to U by applying a function to a contained `Ok`
           value, or a fallback function to a contained `Error` value.
        """
        return NotImplemented

    @abstractmethod
    def map_err(
        self, fn: Callable[[ValueType], ValueType]
    ) -> Union[Result[ValueType, ErrorType], Result[ValueType, F]]:
        """Maps a Result(T, E) to Result(T, F) by applying a function to a
           contained `Error` value, leaving an `Ok` value untouched.
        """
        return NotImplemented

    @abstractmethod
    def unwrap(self) -> Union[ValueType, ErrorType]:
        """Returns the `Ok` value if `self` is `Ok` and the `Error` value if
           `self` is an `Error`
        """
        return NotImplemented
