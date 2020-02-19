import decimal
import datetime

from dynamo_query.json_tools import dumps, loads


class TestJSONTools:
    @staticmethod
    def test_dumps() -> None:
        class NonSerializeable:
            def __repr__(self) -> str:
                return "NonSerializeable class"

        data = dict(
            int=decimal.Decimal("12"),
            float=decimal.Decimal("0.5"),
            cls=NonSerializeable(),
            str="string",
            set={1, 2, 3},
            datetime=datetime.datetime(2020, 1, 15, 14, 34, 56),
            date=datetime.date(2020, 1, 15),
            exc=ValueError("test"),
        )
        json_data = dumps(data)
        assert loads(json_data) == dict(
            int=12,
            float=0.5,
            cls="NonSerializeable class",
            str="string",
            set=[1, 2, 3],
            datetime="2020-01-15T14:34:56Z",
            date="2020-01-15",
            exc="ValueError('test')",
        )

    @staticmethod
    def test_loads() -> None:
        data = (
            "{\"cls\": \"<module 'decimal' from '/usr/lib/python3.7/decimal.py'>\", "
            '"float": 0.5, "int": 12, "str": "string"}'
        )
        result = loads(data)
        assert result == {
            "cls": "<module 'decimal' from '/usr/lib/python3.7/decimal.py'>",
            "float": 0.5,
            "int": 12,
            "str": "string",
        }
