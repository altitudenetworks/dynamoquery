from decimal import Decimal
from typing import Any, Callable, Optional, TypeVar

_S = TypeVar("_S", bound="KeySanitizer")
_C = TypeVar("_C", bound="KeyComputer")


class KeySanitizer:
    def __init__(self, key: str) -> None:
        self.key = key
        self.method: Optional[Callable[..., Any]] = None

    def __call__(self: _S, method: Callable[..., Any]) -> _S:
        self.method = method
        return self

    def sanitize(self, instance: Any, value: Any, **kwargs: Any) -> Any:
        if not self.method:
            raise ValueError(f"KeySanitizer for {self.key} is not initialized")
        return self.method(instance, value=value, **kwargs)


class KeyComputer:
    def __init__(self, key: str) -> None:
        self.key = key
        self.method: Optional[Callable[[Any], Any]] = None

    def __call__(self: _C, method: Callable[[Any], Any]) -> _C:
        self.method = method
        return self

    def compute(self, instance: Any) -> Any:
        if not self.method:
            raise ValueError(f"KeyComputer for {self.key} is not initialized")
        return self.method(instance)


class DecimalSanitizer(KeySanitizer):
    def sanitize(self, instance: Any, value: Any, **kwargs: Any) -> Any:
        allowed_types = instance.allowed_types.get(self.key)
        if allowed_types and isinstance(value, Decimal):
            if float in allowed_types:
                return float(value)
            if int in allowed_types:
                return int(value)

        return value
