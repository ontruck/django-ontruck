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

    def __bool__(self) -> bool:
        return self.is_ok()

    @abstractmethod
    def is_ok(self) -> bool:
        """Returns True if `self` is an `Ok`
        """
        raise NotImplementedError()

    @abstractmethod
    def is_error(self) -> bool:
        """Returns True if `self` is an `Error`
        """
        raise NotImplementedError()

    @abstractmethod
    def and_then(
        self, fn: Callable[[ValueType], Result[ValueType, ErrorType]]
    ) -> Result[ValueType, ErrorType]:
        """Calls `fn` if the result is `Ok`, otherwise returns the `Error`
           value of `self`.
        """
        raise NotImplementedError()

    @abstractmethod
    def or_else(
        self, fn: Callable[[ValueType], Result[ValueType, ErrorType]]
    ) -> Result[ValueType, ErrorType]:
        """Calls `fn` if the result is `Error`, otherwise returns the `Ok`
           value of `self`
        """
        raise NotImplementedError()

    @abstractmethod
    def unwrap_or(self, default: ValueType) -> ValueType:
        """Returns a contained `Ok` value or a provided default.
        """
        raise NotImplementedError()

    @abstractmethod
    def unwrap_or_else(
        self, fn: Callable[[ValueType], ValueType]
    ) -> ValueType:
        """Return the contained `Ok` value or computes it from a closure.
        """
        raise NotImplementedError()

    @abstractmethod
    def map(
        self, fn: Callable[[ValueType], Result[U, ErrorType]]
    ) -> Union[Result[ValueType, ErrorType], Result[U, ErrorType]]:
        """Maps Result(T, E) to Result(U, E) by applying a function to a
           contained `Ok` value, leaving an `Error` value untouched.
        """
        raise NotImplementedError()

    def __or__(
        self,
        fn: Callable[[ValueType], Result[U, ErrorType]]
    ) -> Union[Result[ValueType, ErrorType], Result[U, ErrorType]]:
        return self.map(fn)

    @abstractmethod
    def map_or(
        self,
        fn: Callable[[ValueType], ValueType],
        default: Optional[ValueType] = None
    ) -> Optional[ValueType]:
        """Applies a function to the contained value if `Ok`, or return the
           provided default if `Error`
        """
        raise NotImplementedError()

    @abstractmethod
    def map_or_else(
        self, fn: Callable[[ValueType], U], defaultfn: Callable[[ValueType], U]
    ) -> U:
        """Maps a Result(T, E) to U by applying a function to a contained `Ok`
           value, or a fallback function to a contained `Error` value.
        """
        raise NotImplementedError()

    @abstractmethod
    def map_err(
        self, fn: Callable[[ValueType], ValueType]
    ) -> Union[Result[ValueType, ErrorType], Result[ValueType, F]]:
        """Maps a Result(T, E) to Result(T, F) by applying a function to a
           contained `Error` value, leaving an `Ok` value untouched.
        """
        raise NotImplementedError()

    @abstractmethod
    def unwrap(self) -> Union[ValueType, ErrorType]:
        """Returns the `Ok` value if `self` is `Ok` and the `Error` value if
           `self` is an `Error`
        """
        raise NotImplementedError()
