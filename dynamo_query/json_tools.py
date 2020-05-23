"""
# JSON Tools

Safe JSON SerDe.
"""
import datetime
import decimal
import json
from typing import Any, Type


class SafeJSONEncoder(json.JSONEncoder):
    """
    Safe encoder for `json.dumps`. Handles `decimal.Decimal`
    values properly and uses `repr` for any non-serializeable object.

    - set is serialized to list
    - date is serialized to a string in "%Y-%m-%d" format
    - datetime is serialized to a string in "%Y-%m-%dT%H:%M:%SZ" format
    - integral Decimal is serialized to int
    - non-integral Decimal is serialized to float
    - Exception is serialized to string
    - Unknown type is serialized to string as a repr

    ```python
    data = {
        'string': 'test',
        'decimal': decimal.Decimal('3.14'),
        'datetime': datetime.datetime(2020, 1, 15, 14, 34, 56),
        'date': datetime.date(2020, 1, 15),
        'exception': ValueError('test'),
    }
    json.dumps(data, cls=SafeJSONEncoder)
    ```
    """

    iso_format = r"%Y-%m-%dT%H:%M:%SZ"
    simple_date_format = r"%Y-%m-%d"

    def default(self, o: Any) -> Any:  # pylint:disable=method-hidden
        """
        Override handling of non-JSON-serializeable objects.
        Supports `decimal.Decimal` and `set`.

        Arguments:
            o -- Object for serialization.

        Returns:
            `int` or `float` for decimal values, otherwise a string with object representation.
        """
        if isinstance(o, decimal.Decimal):
            if o == o.to_integral_value():
                return int(o)

            return float(o)

        if isinstance(o, set):
            return list(o)

        if isinstance(o, datetime.datetime):
            return o.strftime(self.iso_format)

        if isinstance(o, datetime.date):
            return o.strftime(self.simple_date_format)

        if isinstance(o, BaseException):
            return f"{o.__class__.__name__}('{o}')"

        return repr(o)


def dumps(
    data: Any, sort_keys: bool = True, cls: Type[json.JSONEncoder] = SafeJSONEncoder, **kwargs: Any,
) -> str:
    """
        Alias for `json.dumps`. Uses `SafeJSONEncoder` to serialize
        Decimals and non-serializeable objects. Sorts dict keys by default.

        Arguments:
            data -- JSON-serializeable object.
            sort_keys -- Sort output of dictionaries by key.
            cls -- JSON encoder for Python data structures.
            kwargs -- List of additional parameters to pass to `json.dumps`.

        Returns:
            A string with serialized JSON.
    """
    return json.dumps(data, sort_keys=sort_keys, cls=cls, **kwargs,)


def loads(data: str, **kwargs: Any) -> Any:
    """
    Alias for `json.loads`.

    Arguments:
        data -- A string with valid JSON.
        kwargs -- List of additional parameters to pass to `json.loads`.

    Returns:
        An object created from JSON data.
    """
    return json.loads(data, **kwargs)
