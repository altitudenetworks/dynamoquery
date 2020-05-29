import inspect
from collections import UserDict
from copy import deepcopy
from decimal import Decimal
from typing import Any, Dict, List, Tuple

__all__ = ("DynamoRecord", "NullableDynamoRecord")


class DynamoRecord(UserDict):
    """
    Dict-based wrapper for DynamoDB records.

    Examples:

        ```python
        class UserRecord(DynamoRecord):
            # required fields
            name: str

            # optional fields
            company: str = "Amazon"
            age: Optional[int] = None

            def __post_init__(self):
                # do any post-init operations here
                self.age = self.age or 35

        record = UserRecord(name="Jon")
        record["age"] = 30
        record.age = 30
        record.update({"age": 30})

        dict(record) # {"name": "Jon", "company": "Amazon", "age": 30}
        ```
    """

    # Marker for optional fields with no initial value, oerride to None if needed
    NOT_SET: Any = None

    # KeyError is raised if unknown key provided
    SKIP_UNKNOWN_KEYS: bool = True

    # Prefix for copluted key method names
    COMPUTED_KEY_PREFIX: str = "get_key_"

    def __init__(self, *args: Dict[str, Any], **kwargs: Any) -> None:
        super().__init__()
        self._computed_field_names = self._get_computed_field_names()
        self._local_members = self._get_local_members()
        self._allowed_types = self._get_allowed_types(self._local_members["__annotations__"])
        del self._local_members["__annotations__"]

        self._required_field_names = self._get_required_field_names()
        self._field_names = self._get_field_names()
        self.data.clear()
        self._init_data(*args, kwargs)
        self.__post_init__()

    def __post_init__(self) -> None:
        """
        Override this method for post-init operations
        """

    @staticmethod
    def _get_allowed_types(annotations: Dict[str, Any]) -> Dict[str, Tuple[Any, ...]]:
        result: Dict[str, Tuple[Any, ...]] = {}
        for key, annotation in annotations.items():
            if inspect.isclass(annotation):
                result[key] = (annotation,)
                continue

            child_types: Tuple[Any, ...] = tuple()

            if hasattr(annotation, "__args__"):
                child_types = tuple([i for i in annotation.__args__ if inspect.isclass(i)])

            annotation_str = str(annotation)
            if annotation_str.startswith("typing.Dict"):
                result[key] = (dict,)
            if annotation_str.startswith("typing.List"):
                result[key] = (list,)
            if annotation_str.startswith("typing.Set"):
                result[key] = (set,)
            if annotation_str.startswith("typing.Union"):
                result[key] = child_types
            if annotation_str.startswith("typing.Optional"):
                result[key] = (*child_types, None)

        return result

    @classmethod
    def _get_computed_field_names(cls) -> List[str]:
        result = []
        for name, member in inspect.getmembers(cls):
            if name.startswith(cls.COMPUTED_KEY_PREFIX) and inspect.isfunction(member):
                result.append(name.replace(cls.COMPUTED_KEY_PREFIX, "", 1))

        return result

    @classmethod
    def _get_local_members(cls) -> Dict[str, Any]:
        base_field_names = {i[0] for i in inspect.getmembers(DynamoRecord)}
        result: Dict[str, Any] = {
            "__annotations__": {},
        }
        for key, value in inspect.getmembers(cls):
            if key == "__annotations__":
                result["__annotations__"].update(value)
                continue
            if key in base_field_names or inspect.isfunction(value):
                continue
            result[key] = value

        for base_class in cls.__bases__:
            if base_class is DynamoRecord:
                return result
            for key, value in inspect.getmembers(base_class):
                if key == "__annotations__":
                    result["__annotations__"].update(value)
                    continue
                if key in base_field_names or key in result or inspect.isfunction(value):
                    continue
                result[key] = value

        return result

    def _get_required_field_names(self) -> List[str]:
        result = []
        for key in self._allowed_types:
            if key in self._local_members or key.startswith("_"):
                continue

            result.append(key)
        return result

    def _get_field_names(self) -> List[str]:
        result = []
        for key in self._allowed_types:
            if key in self._local_members or key.startswith("_"):
                continue

            result.append(key)

        for key in self._local_members:
            if key.startswith("_"):
                continue

            result.append(key)

        return result

    def _init_data(self, *mappings: Dict[str, Any]) -> None:
        for member_name, member in self._local_members.items():
            if (
                member_name not in self._field_names
                or member is self.NOT_SET
                or isinstance(member, property)
            ):
                continue

            self.data[member_name] = deepcopy(member)

        for mapping in mappings:
            for key, value in mapping.items():
                if key not in self._field_names:
                    if not self.SKIP_UNKNOWN_KEYS:
                        raise KeyError(f"{self._class_name}.{key} does not exist, got {value}.")

                    continue

                value = self._fix_decimal(key, value)
                allowed_types = self._allowed_types.get(key)
                if allowed_types and not isinstance(value, allowed_types):
                    raise ValueError(
                        f"{self._class_name}.{key} has type {allowed_types}, got {repr(value)}."
                    )
                self.data[key] = value

        for key in self._required_field_names:
            if key not in self.data:
                raise ValueError(f"{self._class_name}.{key} must be set.")

        for key in self._computed_field_names:
            self.data[key] = getattr(self, f"{self.COMPUTED_KEY_PREFIX}{key}")()

        for key, value in list(self.data.items()):
            if value is self.NOT_SET:
                del self.data[key]

        self._update_computed()

    def _fix_decimal(self, key: str, value: Any) -> Any:
        if not isinstance(value, Decimal):
            return value

        allowed_types = self._allowed_types.get(key, tuple())
        if float in allowed_types:
            return float(value)

        return int(value)

    @property
    def _class_name(self) -> str:
        return self.__class__.__name__

    def _set_item(self, key: str, value: Any) -> None:
        if value is self.NOT_SET:
            if key in self.data:
                del self.data[key]
                self._update_computed()
            return

        value = self._fix_decimal(key, value)
        allowed_types = self._allowed_types.get(key)
        if allowed_types and not isinstance(value, allowed_types):
            raise ValueError(
                f"{self._class_name}.{key} has type {allowed_types}, got {repr(value)}."
            )

        self.data[key] = value
        self._update_computed()

    def _update_computed(self) -> None:
        for key in self._computed_field_names:
            value = getattr(self, f"{self.COMPUTED_KEY_PREFIX}{key}")()
            if value is self.NOT_SET:
                if key in self.data:
                    del self.data[key]
            else:
                self.data[key] = value

    def __setitem__(self, key: str, value: Any) -> None:
        if key in self._computed_field_names:
            return

        if key not in self._field_names:
            raise KeyError(f"Key {self._class_name}.{key} is incorrect")

        self._set_item(key, value)

    def __setattr__(self, name: str, value: Any) -> None:
        if hasattr(self, "_computed_field_names") and name in self._computed_field_names:
            raise KeyError(f"Key {self._class_name}.{name} is computed and cannot be set directly")

        if not hasattr(self, "_field_names") or name not in self._field_names:
            super().__setattr__(name, value)
            return

        self._set_item(name, value)

    def __getattribute__(self, name: str) -> Any:
        if name.startswith("_"):
            return super().__getattribute__(name)
        if not hasattr(self, "_field_names") or name not in self._field_names:
            return super().__getattribute__(name)

        return self.data.get(name, self.NOT_SET)

    def __str__(self) -> str:
        return f"{self._class_name}({self.data})"


class NullableDynamoRecord(UserDict):
    """
    DynamoRecord that allows `None` values
    """

    NOT_SET: Any = object()
