# DynamoRecord

> Auto-generated documentation for [dynamo_query.dynamo_record](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_record.py) module.

- [dynamo-query](../README.md#dynamoquery) / [Modules](../MODULES.md#dynamo-query-modules) / [Dynamo Query](index.md#dynamo-query) / DynamoRecord
    - [DynamoRecord](#dynamorecord)
        - [DynamoRecord().\_\_post\_init\_\_](#dynamorecord__post_init__)
        - [DynamoRecord().sanitize](#dynamorecordsanitize)
        - [DynamoRecord().sanitize_key](#dynamorecordsanitize_key)
    - [NullableDynamoRecord](#nullabledynamorecord)

## DynamoRecord

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_record.py#L10)

```python
class DynamoRecord(UserDict):
    def __init__(*args: Dict[str, Any], **kwargs: Any) -> None:
```

Dict-based wrapper for DynamoDB records.

#### Examples

```python
class UserRecord(DynamoRecord):
    # required fields
    name: str

    # optional fields
    company: str = "Amazon"
    age: Optional[int] = None

    def __post_init__(self):
        # do any post-init operations here
        self.age = self.age or 35

    # add extra computed field
    def get_key_min_age(self) -> int:
        return 18

    # sanitize value on set
    def sanitize_key_age(self, value: int) -> int:
        return max(self.age, 18)

record = UserRecord(name="Jon")
record["age"] = 30
record.age = 30
record.update({"age": 30})

dict(record) # {"name": "Jon", "company": "Amazon", "age": 30, "min_age": 18}
```

### DynamoRecord().\_\_post\_init\_\_

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_record.py#L72)

```python
def __post_init__() -> None:
```

Override this method for post-init operations

### DynamoRecord().sanitize

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_record.py#L302)

```python
def sanitize(**kwargs: Any) -> None:
```

Sanitize all set fields.

#### Arguments

- `kwargs` - Arguments for sanitize_key_{key}

### DynamoRecord().sanitize_key

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_record.py#L268)

```python
def sanitize_key(key: str, value: Any, **kwargs: Any) -> Any:
```

Sanitize value before putting it to dict.

- Converts decimals to int/float
- Calls `sanitize_key_{key}` method if it is defined
- Checks if sanitized value has a proper type

#### Arguments

- `key` - Dictionary key
- `value` - Raw value

#### Returns

A sanitized value

## NullableDynamoRecord

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_record.py#L315)

```python
class NullableDynamoRecord(UserDict):
```

DynamoRecord that allows `None` values
