import pytest

from dynamo_query.utils import (
    chunkify,
    ascii_string_generator,
    get_format_keys,
    pluralize,
    get_nested_item,
)


class TestUtils:
    @staticmethod
    def test_chunkify() -> None:
        data = [1, 2, 3, 4, 5]
        assert list(chunkify(data, size=2)) == [[1, 2], [3, 4], [5]]
        assert list(chunkify([], size=2)) == []

        generator = chunkify(data, size=2)
        assert next(generator) == [1, 2]
        assert next(generator) == [3, 4]
        assert next(generator) == [5]

        with pytest.raises(StopIteration):
            next(generator)

    @staticmethod
    def test_ascii_string_generator() -> None:
        gen = ascii_string_generator(length=2)
        assert next(gen) == "aa"
        assert next(gen) == "ab"
        assert list(gen)[-1] == "zz"

        gen = ascii_string_generator(length=3)
        assert next(gen) == "aaa"

    @staticmethod
    def test_get_format_keys() -> None:
        assert get_format_keys("{} key: {key} {value}") == {"key", "value"}
        assert get_format_keys("string") == set()

    @staticmethod
    def test_pluralize() -> None:
        assert pluralize(1, "item") == "item"
        assert pluralize(5, "item") == "items"
        assert pluralize(1, "cactus", "cacti") == "cactus"
        assert pluralize(5, "cactus", "cacti") == "cacti"

    @staticmethod
    def test_get_nested_item() -> None:
        nested_dict = {"a": {"b": {"c": 1}}}
        assert get_nested_item(nested_dict, ["a", "b", "c"]) == 1
        assert get_nested_item(nested_dict, ["a", "b"]) == {"c": 1}
        assert get_nested_item(nested_dict, ["a", "c"]) is None
        assert get_nested_item(nested_dict, ["b", "c"]) is None

        assert get_nested_item(nested_dict, ["a", "c"], raise_errors=True) is None
        with pytest.raises(AttributeError):
            get_nested_item(nested_dict, ["b", "c"], raise_errors=True)
