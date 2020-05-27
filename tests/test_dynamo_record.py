from typing import Any, Optional

import pytest

from dynamo_query.dynamo_record import DynamoRecord


class MyRecord(DynamoRecord):
    name: str
    age: Optional[int] = None

    def age_next(self) -> int:
        return (self.age or 0) + 1


class NewRecord(MyRecord):
    last_name: str
    any_data: Any = "any_data"

    COMPUTED_FIELDS = ["age_next"]

    @property
    def age_prop(self) -> int:
        return (self.age or 0) + 1


class TestDynamoRecord:
    def test_init(self):
        my_record = MyRecord(name="test")
        assert my_record.name == "test"
        assert my_record.age is None
        assert my_record.age_next() == 1
        assert dict(my_record) == {"name": "test"}
        assert str(my_record) == "MyRecord({'name': 'test'})"
        assert list(my_record.keys()) == ["name"]
        assert list(my_record.items()) == [("name", "test")]
        assert my_record == MyRecord(name="test")

        my_record.name = "test2"
        my_record.age = 42
        assert my_record.age_next() == 43
        assert dict(my_record) == {"name": "test2", "age": 42}

        my_record["age"] = 12
        my_record["name"] = "test3"
        assert dict(my_record) == {"name": "test3", "age": 12}

        my_record2 = MyRecord(my_record, {"age": None})
        assert my_record2.age == None
        assert my_record2 == {"name": "test3"}
        my_record2.update({"age": 13})
        assert dict(my_record2) == {"name": "test3", "age": 13}

        with pytest.raises(KeyError):
            my_record2["unknown"] = "test"

        with pytest.raises(ValueError):
            my_record2["name"] = 13

        with pytest.raises(ValueError):
            my_record2.age = "test"

        with pytest.raises(ValueError):
            MyRecord({"name": 12})

    def test_inherited(self):
        new_record = NewRecord(name="test1", last_name="test")
        assert new_record == {
            "name": "test1",
            "last_name": "test",
            "age_next": 1,
            "any_data": "any_data",
        }

        new_record.age = 12
        new_record.any_data = 14
        assert new_record == {
            "name": "test1",
            "last_name": "test",
            "age": 12,
            "age_next": 13,
            "any_data": 14,
        }
        new_record.age = None

        with pytest.raises(ValueError):
            NewRecord(last_name="test")

        with pytest.raises(ValueError):
            NewRecord(name="test")

        with pytest.raises(ValueError):
            NewRecord({"name": 12})
