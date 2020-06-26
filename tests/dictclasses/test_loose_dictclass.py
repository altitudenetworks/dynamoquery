import pytest

from dynamo_query.dictclasses.loose_dictclass import LooseDictClass


class MyLooseDictClass(LooseDictClass):
    required: int
    value: int = 5

    @LooseDictClass.compute_key("computed")
    def get_computed(self) -> str:
        return "test"


class TestLooseDictClass:
    def test_init(self):
        result = MyLooseDictClass(required=1, new="test")
        assert result == {"new": "test", "required": 1, "value": 5, "computed": "test"}

        result["new"] = "asd"
        result["newest"] = "asd"
        result.update({"other": "test"})

        with pytest.raises(KeyError):
            result["computed"] = "new"

        with pytest.raises(ValueError):
            MyLooseDictClass(new="test")

        assert MyLooseDictClass(required=1).required == 1
        with pytest.raises(AttributeError):
            MyLooseDictClass(required=1).test
        with pytest.raises(KeyError):
            MyLooseDictClass(required=1)["test"]
