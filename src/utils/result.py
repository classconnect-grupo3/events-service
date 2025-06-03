from typing import Generic, TypeVar

T = TypeVar("T")


class Result(Generic[T]):
    pass


class Success(Result):
    def __init__(self, value: T):
        self.value = value


class Failure(Result):
    def __init__(self, error: Exception):
        self.error = error
