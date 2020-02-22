# Utils

> Auto-generated documentation for [dynamo_query.utils](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/utils.py) module.

- [dynamo-query](../README.md#dynamo-query) / [Modules](../MODULES.md#dynamo-query-modules) / [Dynamo Query](index.md#dynamo-query) / Utils
    - [ascii_string_generator](#ascii_string_generator)
    - [chunkify](#chunkify)
    - [get_format_keys](#get_format_keys)
    - [get_nested_item](#get_nested_item)
    - [pluralize](#pluralize)

## ascii_string_generator

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/utils.py#L37)

```python
def ascii_string_generator(length: int = 3) -> Iterator[str]:
```

Generator to build unique strings from "aa...a" to "zz...z".

```python
gen = ascii_string_generator()
next(gen)  # 'aaa'
next(gen)  # 'aab'
list(gen)[-1]  # 'zzz'
```

#### Arguments

- `length` - Length of a result string.

#### Yields

Lowercased ASCII string like "aaa"

## chunkify

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/utils.py#L5)

```python
def chunkify(data: Iterable, size: int) -> Iterator[List[Any]]:
```

Splits data to chunks of `size` length or less.

```python
data = [1, 2, 3, 4, 5]
for chunk in chunkify(data, size=2):
    print(chunk)

# [1, 2]
# [3, 4]
# [5]
```

#### Arguments

- `data` - Data to chunkify
- `size` - Max chunk size.

#### Returns

A generator of chunks.

## get_format_keys

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/utils.py#L67)

```python
def get_format_keys(format_string: str) -> Set[str]:
```

Extract format keys from a formet-ready string.

```python
keys = get_format_keys('key: {key} {value}')
keys # ['key', 'value']
```

#### Arguments

- `format_string` - A format-ready string.

#### Returns

A set of format keys.

## get_nested_item

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/utils.py#L112)

```python
def get_nested_item(
    dict_obj: Dict[str, Any],
    item_path: Iterable[str],
    raise_errors: bool = False,
) -> Any:
```

Get nested `item_path` from `dict_obj`.

#### Arguments

- `dict_obj` - Source dictionary.
- `item_path` - Keys list.
- `raise_errors` - Whether to raise `AttributeError` on not a dictionary item.

#### Raises

- `AttributeError` - If nested item is not a dictionary.

## pluralize

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/utils.py#L91)

```python
def pluralize(count: int, singular: str, plural: Optional[str] = None) -> str:
```

Pluralize a noun according to `count`.

#### Arguments

- `count` - Count of objects.
- `singular` - Singular noun form.
- `plural` - Plural noun form. If not provided - append `s` to singular form.

#### Returns

A noun in proper form.
