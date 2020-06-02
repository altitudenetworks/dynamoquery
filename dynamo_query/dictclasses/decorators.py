from functools import wraps
from typing import Any, Callable, TypeVar

_R = TypeVar("_R")


class KeySanitizer:
    def __init__(self, key: str) -> None:
        self.key = key

    def __call__(self, method: Callable[..., _R]) -> Callable[..., _R]:
        @wraps(method)
        def wrapper(instance: Any, value: Any, **kwargs: Any) -> _R:
            return method(instance, value, **kwargs)

        setattr(wrapper, "KeySanitizer", self)

        return wrapper


class KeyComputer:
    def __init__(self, key: str) -> None:
        self.key = key

    def __call__(self, method: Callable[..., _R]) -> Callable[..., _R]:
        @wraps(method)
        def wrapper(instance: Any) -> _R:
            return method(instance)

        setattr(wrapper, "KeyComputer", self)

        return wrapper
