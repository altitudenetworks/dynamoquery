# Sentinel

> Auto-generated documentation for [dynamo_query.sentinel](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/sentinel.py) module.

Sentinel value than can be used as a placeholder.

- [dynamo-query](../README.md#dynamo-query) / [Modules](../MODULES.md#dynamo-query-modules) / [Dynamo Query](index.md#dynamo-query) / Sentinel
    - [SentinelValue](#sentinelvalue)

## SentinelValue

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/sentinel.py#L5)

```python
class SentinelValue():
    def __init__(name: str = 'DEFAULT') -> None:
```

Sentinel value than can be used as a placeholder.
Doc generation friendly.

```python
NOT_SET = SentinelValue('NOT_SET')

def check_value(name=NOT_SET):
    if name is NOT_SET:
        return 'This is a NOT_SET value'

    return 'This is something else'

repr(NOT_SET) # 'NOT_SET'
```

#### Arguments

- `name` - String used as a representation of the object.
