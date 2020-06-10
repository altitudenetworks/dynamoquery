import inspect
from collections import UserDict
from copy import copy
from typing import Any, Callable, Dict, List, Tuple, Type, TypeVar, cast

from dynamo_query.dictclasses.decorators import KeyComputer, KeySanitizer

__all__ = ("DictClass",)


_R = TypeVar("_R", bound="DictClass")


class DictClass(UserDict):
    """
    Dict-based dataclass.

    Examples:

        ```python
        class UserRecord(DictClass):
            # required fields
            name: str

            # optional fields
            company: str = "Amazon"
            age: Optional[int] = None

            def __post_init__(self):
                # do any post-init operations here
                self.age = self.age or 35

            # add extra computed field
            @DictClass.compute_key("min_age")
            def _compute_min_age(self) -> int:
                return 18

            # sanitize value on set
            @DictClass.sanitize_key("age")
            def _sanitize_key_age(self, value: int) -> int:
                return max(self.age, 18)

        record = UserRecord(name="Jon")
        record["age"] = 30
        record.age = 30
        record.update({"age": 30})

        dict(record) # {"name": "Jon", "company": "Amazon", "age": 30, "min_age": 18}
        ```
    """

    # Marker for optional fields with no initial value, set to None if needed
    NOT_SET: Any = object()

    # KeyError is raised if unknown key provided
    RAISE_ON_UNKNOWN_KEY: bool = False

    _initialized_classes: List[int] = []
    _local_members_cache: Dict[int, Dict[str, Any]] = {}
    _local_members: Dict[str, Any] = {}
    _sanitizers: Dict[str, List[Callable[..., Any]]] = {}
    _computers: Dict[str, Callable[[Any], Any]] = {}
    _allowed_types: Dict[str, Tuple[Any, ...]] = {}
    _required_field_names: List[str] = []
    _field_names: List[str] = []

    def __new__(cls: Type[_R], *args: Dict[str, Any], **kwargs: Any) -> _R:
        instance = super().__new__(cls)
        cls._initalize_class()
        instance.__init__(*args, **kwargs)
        return cast(_R, instance)

    @classmethod
    def _initalize_class(cls) -> None:
        if id(cls) in cls._initialized_classes:
            return

        cls._local_members = cls._get_local_members()
        cls._sanitizers = cls._get_sanitizers()
        cls._computers = cls._get_computers()
        cls._allowed_types = cls._get_allowed_types()
        cls._initialized_classes.append(id(cls))
        cls._required_field_names = cls._get_required_field_names()
        cls._field_names = cls._get_field_names()

    def __init__(self, *args: Dict[str, Any], **kwargs: Any) -> None:
        super().__init__()
        self.data.clear()
        self._init_data(*args, kwargs)
        self.__post_init__()

    def __post_init__(self) -> None:
        """
        Override this method for post-init operations
        """

    @classmethod
    def _get_sanitizers(cls) -> Dict[str, List[Callable[..., Any]]]:
        result: Dict[str, List[Callable[..., Any]]] = {}
        for member in cls._local_members.values():
            if not inspect.isfunction(member):
                continue

            sanitizer = getattr(member, "KeySanitizer", None)
            if not sanitizer:
                continue

            if sanitizer.key not in result:
                result[sanitizer.key] = []

            result[sanitizer.key].append(member)

        return result

    @classmethod
    def _get_computers(cls) -> Dict[str, Callable[[Any], Any]]:
        result: Dict[str, Callable[[Any], Any]] = {}
        for member in cls._local_members.values():
            if not inspect.isfunction(member):
                continue

            computer = getattr(member, "KeyComputer", None)
            if not computer:
                continue
            result[computer.key] = member

        return result

    @staticmethod
    def sanitize_key(key: str) -> KeySanitizer:
        return KeySanitizer(key)

    @staticmethod
    def compute_key(key: str) -> KeyComputer:
        return KeyComputer(key)

    @classmethod
    def _get_allowed_types(cls) -> Dict[str, Tuple[Any, ...]]:
        result: Dict[str, Tuple[Any, ...]] = {}
        annotations = cls._local_members.get("__annotations__", {})
        for key, annotation in annotations.items():
            annotation_str = str(annotation)
            if not annotation_str.startswith("typing.") and inspect.isclass(annotation):
                result[key] = (annotation,)
                continue

            child_types: Tuple[Any, ...] = tuple()

            if hasattr(annotation, "__args__"):
                child_types = tuple([i for i in annotation.__args__ if inspect.isclass(i)])

            result[key] = tuple()
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
    def _get_local_members(cls) -> Dict[str, Any]:
        base_field_names = {i[0] for i in inspect.getmembers(DictClass)}
        result: Dict[str, Any] = {
            "__annotations__": {},
        }
        for key, value in inspect.getmembers(cls):
            if key == "__annotations__":
                result["__annotations__"].update(value)
                continue
            if key in base_field_names:
                continue
            result[key] = value

        for base_class in cls.__bases__:
            if base_class is DictClass:
                return result
            for key, value in inspect.getmembers(base_class):
                if key == "__annotations__":
                    result["__annotations__"].update(value)
                    continue
                if key in base_field_names or key in result:
                    continue
                result[key] = value

        return result

    @classmethod
    def _get_required_field_names(cls) -> List[str]:
        result = []
        for key in cls._allowed_types:
            if key in cls._local_members:
                continue

            if key.startswith("_") or key.upper() == key:
                continue

            result.append(key)
        return result

    @classmethod
    def _get_field_names(cls) -> List[str]:
        result = []
        for key in cls._allowed_types:
            if key in cls._local_members:
                continue

            if key.startswith("_") or key.upper() == key:
                continue

            result.append(key)

        for key, value in cls._local_members.items():
            if key.startswith("_") or key.upper() == key:
                continue

            if inspect.isfunction(value) or inspect.ismethod(value) or isinstance(value, property):
                continue

            result.append(key)

        return result

    def _init_data(self, *mappings: Dict[str, Any]) -> None:
        for key, member in self._local_members.items():
            if key not in self._field_names:
                continue

            self.data[key] = copy(member)

        for mapping in mappings:
            for key, value in mapping.items():
                if key in self._computers:
                    continue

                if key not in self._field_names:
                    if self.RAISE_ON_UNKNOWN_KEY:
                        raise KeyError(
                            f"{self._class_name}.{key} does not exist, got value {repr(value)}."
                        )

                    continue

                self.data[key] = value

        for key in self._field_names:
            self.data[key] = self._sanitize_key(key, self.data.get(key, self.NOT_SET))

        for key, value in list(self.data.items()):
            if value is self.NOT_SET:
                del self.data[key]

        for key in self._required_field_names:
            if key not in self.data:
                raise ValueError(f"{self._class_name}.{key} must be set: {self.data}")

        self._update_computed()

    @property
    def _class_name(self) -> str:
        return self.__class__.__name__

    def _set_item(
        self, key: str, value: Any, is_initial: bool, sanitize_kwargs: Dict[str, Any]
    ) -> None:
        sanitized_value = self._sanitize_key(key, value, **sanitize_kwargs)

        if not is_initial:
            if sanitized_value is self.NOT_SET:
                if key in self.data:
                    del self.data[key]
                    self._update_computed()
                return

        self.data[key] = sanitized_value

        if not is_initial:
            self._update_computed()

    def _update_computed(self) -> None:
        for key, computer in self._computers.items():
            value = computer(self)
            if value is self.NOT_SET:
                if key in self.data:
                    del self.data[key]
            else:
                self.data[key] = value

    def __setitem__(self, key: str, value: Any) -> None:
        if key in self._computers:
            return

        if key not in self._field_names:
            raise KeyError(f"Key {self._class_name}.{key} is incorrect")

        self._set_item(key, value, is_initial=False, sanitize_kwargs={})

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "data":
            super().__setattr__(name, value)
            return

        if name in self._computers:
            raise KeyError(f"Key {self._class_name}.{name} is computed and cannot be set directly")

        if name not in self._field_names:
            super().__setattr__(name, value)
            return

        self._set_item(name, value, is_initial=False, sanitize_kwargs={})

    def __getattribute__(self, name: str) -> Any:
        if name == "data":
            return super().__getattribute__("data")
        if name.startswith("_"):
            return super().__getattribute__(name)
        if not hasattr(self, "_field_names") or name not in self._field_names:
            return super().__getattribute__(name)

        return self.data.get(name, self.NOT_SET)

    def __str__(self) -> str:
        return f"{self._class_name}({self.data})"

    def _sanitize_key(self, key: str, value: Any, **kwargs: Any) -> Any:
        """
        Sanitize value before putting it to dict.

        Calls `sanitize_key_{key}` method if it is defined

        Arguments:
            key -- Dictionary key
            value -- Raw value

        Returns:
            A sanitized value
        """
        for sanitizer in self._sanitizers.get(key, []):
            value = sanitizer(self, value, **kwargs)

        return value

    def sanitize(self, **kwargs: Any) -> None:
        """
        Sanitize all set fields.

        Arguments:
            kwargs -- Arguments for sanitize_key_{key}
        """
        for key in self._sanitizers:
            value = self.get(key, self.NOT_SET)
            self._set_item(key, value, is_initial=False, sanitize_kwargs=kwargs)
