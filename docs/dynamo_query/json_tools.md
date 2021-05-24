# JSON Tools

> Auto-generated documentation for [dynamo_query.json_tools](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/json_tools.py) module.

Safe JSON SerDe.

- [dynamo-query](../README.md#dynamoquery) / [Modules](../MODULES.md#dynamo-query-modules) / [Dynamo Query](index.md#dynamo-query) / JSON Tools
    - [SafeJSONEncoder](#safejsonencoder)
        - [SafeJSONEncoder().default](#safejsonencoderdefault)
    - [dumps](#dumps)
    - [loads](#loads)

## SafeJSONEncoder

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/json_tools.py#L12)

```python
class SafeJSONEncoder(json.JSONEncoder):
```

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

### SafeJSONEncoder().default

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/json_tools.py#L40)

```python
def default(o: Any) -> Any:
```

Override handling of non-JSON-serializeable objects.
Supports `decimal.Decimal` and `set`.

#### Arguments

- `o` - Object for serialization.

#### Returns

`int` or `float` for decimal values, otherwise a string with object representation.

## dumps

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/json_tools.py#L72)

```python
def dumps(
    data: Any,
    sort_keys: bool = True,
    cls: Type[json.JSONEncoder] = SafeJSONEncoder,
    **kwargs: Any,
) -> str:
```

Alias for `json.dumps`. Uses [SafeJSONEncoder](#safejsonencoder) to serialize
Decimals and non-serializeable objects. Sorts dict keys by default.

#### Arguments

- `data` - JSON-serializeable object.
- `sort_keys` - Sort output of dictionaries by key.
- `cls` - JSON encoder for Python data structures.
- `kwargs` - List of additional parameters to pass to `json.dumps`.

#### Returns

A string with serialized JSON.

#### See also

- [SafeJSONEncoder](#safejsonencoder)

## loads

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/json_tools.py#L99)

```python
def loads(data: str, **kwargs: Any) -> Any:
```

Alias for `json.loads`.

#### Arguments

- `data` - A string with valid JSON.
- `kwargs` - List of additional parameters to pass to `json.loads`.

#### Returns

An object created from JSON data.
