from dataclasses import dataclass
from typing import Optional

import pytest

from dynamo_query.dynamo_record import DynamoRecord


@dataclass
class MyRecord(DynamoRecord):
    name: str
    age: Optional[int] = None


@dataclass
class InvalidRecord(DynamoRecord):
    data: str


class TestDynamoRecord:
    def test_init(self):
        my_record = MyRecord(name="test")
        assert my_record.name == "test"
        assert my_record.age is None
        assert dict(my_record) == {"name": "test"}
        assert str(my_record) == "MyRecord({'name': 'test'})"

        my_record.name = "test2"
        my_record.age = 42
        assert dict(my_record) == {"name": "test2", "age": 42}
        assert my_record.asdict() == {"name": "test2", "age": 42}

        my_record["age"] = 12
        my_record["name"] = "test3"
        assert dict(my_record) == {"name": "test3", "age": 12}
        assert my_record.asdict() == {"name": "test3", "age": 12}

        my_record2 = MyRecord.fromdict(my_record, {"age": 15})
        assert my_record2.age == 15
        my_record2.update({"age": 13})
        assert dict(my_record2) == {"name": "test3", "age": 13}
        assert my_record2.asdict() == {"name": "test3", "age": 13}

        my_record2.age = "test"
        my_record2["age"] = "test"
        with pytest.raises(KeyError):
            my_record2["unknown"] = "test"

        with pytest.raises(ValueError):
            my_record2["name"] = 13

        with pytest.raises(KeyError):
            InvalidRecord(data="test")
