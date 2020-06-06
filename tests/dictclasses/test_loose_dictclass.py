from decimal import Decimal
from typing import Any, Dict, List, Optional

import pytest
from dynamo_query.dictclasses.loose_dictclass import LooseDictClass


class MyRecord(LooseDictClass):
    _hidden_required: str
    _hidden: str = "do not show"

    ATTRIBUTE = "my_string"

    name: str
    age: Optional[int] = None


class TestLooseDictClass:
    def test_init(self):
        my_record = MyRecord(name="test", unknown="value")
        assert my_record.get_field_names() == ("name", "age", "unknown")
        assert my_record.get_required_field_names() == ("name",)
