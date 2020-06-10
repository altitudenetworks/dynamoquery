# DynamoDictClass

> Auto-generated documentation for [dynamo_query.dictclasses.dynamo_dictclass](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dictclasses/dynamo_dictclass.py) module.

- [dynamo-query](../../README.md#dynamoquery) / [Modules](../../MODULES.md#dynamo-query-modules) / [Dynamo Query](../index.md#dynamo-query) / [Dictclasses](index.md#dictclasses) / DynamoDictClass
    - [DynamoDictClass](#dynamodictclass)
        - [DynamoDictClass.get_field_names](#dynamodictclassget_field_names)
        - [DynamoDictClass.get_required_field_names](#dynamodictclassget_required_field_names)

## DynamoDictClass

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dictclasses/dynamo_dictclass.py#L7)

```python
class DynamoDictClass(DictClass):
```

#### See also

- [DictClass](dictclass.md#dictclass)

### DynamoDictClass.get_field_names

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dictclasses/dynamo_dictclass.py#L32)

```python
@classmethod
def get_field_names() -> List[str]:
```

Get a list of accepted field names.

#### Returns

A list of field names as strings.

### DynamoDictClass.get_required_field_names

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dictclasses/dynamo_dictclass.py#L21)

```python
@classmethod
def get_required_field_names() -> List[str]:
```

Get a list of required field names.

#### Returns

A list of field names as strings.
