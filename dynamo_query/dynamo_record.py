from dataclasses import dataclass, asdict, fields, Field
from typing import Dict, Any, Iterator, TypeVar, Type, Tuple
from typing import _GenericAlias as GenericAlias  # type: ignore
from collections import UserDict


__all__ = ("DynamoRecord",)


_R = TypeVar("_R", bound="DynamoRecord")


@dataclass
class DynamoRecord(UserDict):
    """
    Dict-based wrapper for DynamoDB records.

    Examples:

        ```python
        @dataclass
        class UserRecord(DynamoRecord):
            # required fields
            name: str

            # optional fields
            age: Optional[int] = None

        record = UserRecord(name="Jon")
        record2 = UserRecord.fromdict({"name": "Jon", "age": 30})
        record2["age"] = 30
        record2.age = 30
        record2.update({"age": 30})

        record.asdict() # {"name": "Jon"}
        record2.asdict() # {"name": "Jon", "age": 30}
        ```
    """

    # Indicator that value is not set and should not appear in dict
    NOT_SET = None

    def __post_init__(self) -> None:
        self.data = self.asdict()
        self._validate_fields()

    def _validate_fields(self) -> None:
        accepted_fields = fields(self)
        field_names = [i.name for i in accepted_fields]
        if "data" in field_names:
            raise KeyError(f"{self._class_name}.data key should not be set directly")
        for key, value in self.data.items():
            self._validate_key(key, value, accepted_fields)

    def asdict(self) -> Dict[str, Any]:
        """
        Get dictionary with set values.

        Examples:

            ```python
            UserRecord(name="test").asdict() # {"name": "test"}
            UserRecord(name="test", "age": 12).asdict() # {"name": "test", "age": 12}
            UserRecord(name="test", age=None) # {"name": "test"}
            ```

        Returns:
            A dictionary.
        """
        return {k: v for k, v in asdict(self).items() if not v is self.NOT_SET}

    @classmethod
    def fromdict(cls: Type[_R], *mappings: Dict[str, Any]) -> _R:
        """
        Equivalent of `DynamoRecord(**my_dict)`

        Arguments:
            mappings -- One or more mappings to extract data.

        Returns:
            A new instance.
        """
        data = {}
        for mapping in mappings:
            data.update(mapping)
        return cls(**data)

    @property
    def _class_name(self) -> str:
        return self.__class__.__name__

    def _validate_key(
        self, key: str, value: Any, accepted_fields: Tuple[Field, ...]
    ) -> None:
        for accepted_field in accepted_fields:
            if accepted_field.name != key:
                continue

            accepted_type = accepted_field.type
            if not isinstance(accepted_type, GenericAlias):
                if not isinstance(value, accepted_type):
                    raise ValueError(
                        f"{self._class_name}.{key} should have type {accepted_type.__name__}, got {value}"
                    )
            return

        raise KeyError(f"Key `{key}` is incorrect for {self._class_name}")

    def __setitem__(self, key: str, value: Any) -> None:
        self._validate_key(key, value, fields(self))
        setattr(self, key, value)

    def __str__(self) -> str:
        return f"{self._class_name}({self.asdict()})"

    def __iter__(self) -> Iterator[str]:
        self.data = self.asdict()
        return super().__iter__()
