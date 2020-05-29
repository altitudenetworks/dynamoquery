from decimal import Decimal
from typing import Any, Dict, List, Optional

import pytest

from dynamo_query.dynamo_record import DynamoRecord


class MyRecord(DynamoRecord):
    _hidden_required: str
    _hidden: str = "do not show"

    ATTRIBUTE = "my_string"

    name: str
    age: Optional[int] = None


class NewRecord(MyRecord):
    last_name: str
    any_data: Any = "any_data"
    percent: Optional[float] = None

    def sanitize_key_age(self, value: int, min_age: int = 10) -> int:
        if value is None:
            return None

        return max(value, min_age)

    def get_key_age_next(self) -> Optional[int]:
        if self.age is None:
            return None
        return self.age + 1

    @property
    def age_prop(self) -> Optional[int]:
        if self.age is None:
            return None
        return self.age + 1


class ImmutableRecord(DynamoRecord):
    RAISE_ON_UNKNOWN_KEY = True

    my_list: List[str] = []
    my_dict: Dict[str, List[str]] = {}

    def get_key_computed(self) -> Optional[str]:
        return "test"


class TestDynamoRecord:
    def test_init(self):
        my_record = MyRecord(name="test")
        assert my_record.name == "test"
        assert my_record.age is None
        assert dict(my_record) == {"name": "test"}
        assert str(my_record) == "MyRecord({'name': 'test'})"
        assert list(my_record.keys()) == ["name"]
        assert list(my_record.items()) == [("name", "test")]
        assert my_record == MyRecord(name="test")

        my_record.name = "test2"
        my_record.age = 42
        assert dict(my_record) == {"name": "test2", "age": 42}

        my_record["age"] = 12
        my_record["name"] = "test3"
        assert dict(my_record) == {"name": "test3", "age": 12}

        my_record2 = MyRecord(my_record, {"age": None})
        assert my_record2.age == None
        assert my_record2 == {"name": "test3"}
        my_record2.update({"age": 13})
        assert dict(my_record2) == {"name": "test3", "age": 13}

        assert MyRecord({"name": "test", "age": Decimal(12.2)}).age == 12
        assert (
            NewRecord({"name": "test", "last_name": "test", "percent": Decimal(12.2)}).percent
            == 12.2
        )
        assert MyRecord({"name": "test", "unknown": 12, "unknown2": 12}) == {"name": "test"}

        with pytest.raises(KeyError):
            my_record2["unknown"] = "test"

        with pytest.raises(ValueError):
            my_record2["name"] = 13

        with pytest.raises(ValueError):
            my_record2.age = "test"

        with pytest.raises(ValueError):
            MyRecord({"name": 12})

    def test_inherited(self):
        new_record = NewRecord(name="test1", last_name="test", age_next=13, unknown="test")
        assert new_record == {
            "name": "test1",
            "last_name": "test",
            "any_data": "any_data",
        }

        with pytest.raises(KeyError):
            new_record["age_next"]

        new_record.age = 12
        new_record.any_data = 14
        assert new_record == {
            "name": "test1",
            "last_name": "test",
            "age": 12,
            "age_next": 13,
            "any_data": 14,
        }

        new_record.age = 8
        assert new_record.age == 10
        assert new_record["age_next"] == 11
        assert NewRecord(name="test1", last_name="test", age=6).age == 10

        new_record.age = None
        assert new_record.age is None

        # fail_record = NewRecord(name="test1", last_name="test", age=14)
        # fail_record["age_next"] = 18
        # raise ValueError(fail_record)

        with pytest.raises(ValueError):
            NewRecord(last_name="test")

        with pytest.raises(ValueError):
            NewRecord(name="test")

        with pytest.raises(ValueError):
            NewRecord({"name": 12, "last_name": "test"})

        with pytest.raises(KeyError):
            new_record.age_next = 14

        with pytest.raises(KeyError):
            new_record["age_next"] = 14

        with pytest.raises(KeyError):
            new_record.update({"age_next": 14})

        assert new_record.get_key_age_next() is None
        new_record["age"] = 15
        assert new_record["age_next"] == 16
        assert new_record.get_key_age_next() == 16
        new_record["age"] = None
        assert "age_next" not in new_record
        assert new_record.get_key_age_next() is None

        new_record = NewRecord(name="test1", last_name="test", age_next=13)
        new_record.update({"age": 66})
        assert new_record["age"] == 66
        assert new_record["age_next"] == 67

    def test_immutability(self):
        record1 = ImmutableRecord(my_dict={"test": ["value"]})
        record2 = ImmutableRecord()
        record1.my_list.extend([1, 2])
        assert record1.my_list == [1, 2]
        assert record2.my_list == []
        assert record1.my_dict == {"test": ["value"]}
        assert record2.my_dict == {}

        ImmutableRecord(computed="new")["computed"] == "test"

        with pytest.raises(ValueError):
            ImmutableRecord(my_dict=[1, 2, 3])

        with pytest.raises(ValueError):
            ImmutableRecord(my_list={1, 2, 3})

        with pytest.raises(KeyError):
            ImmutableRecord(unknown=12)

    def test_sanitize(self):
        record = NewRecord(name="test", last_name="test")
        assert record.age is None
        record.sanitize()
        assert record.age is None
        record.age = 6
        assert record.age == 10
        record.sanitize(min_age=18)
        assert record.age == 18
        record.age = 6
        assert record.age == 10
