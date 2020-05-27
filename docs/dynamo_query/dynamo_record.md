# DynamoRecord

> Auto-generated documentation for [dynamo_query.dynamo_record](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_record.py) module.

- [dynamo-query](../README.md#dynamoquery) / [Modules](../MODULES.md#dynamo-query-modules) / [Dynamo Query](index.md#dynamo-query) / DynamoRecord
    - [DynamoRecord](#dynamorecord)
        - [DynamoRecord().\_\_post\_init\_\_](#dynamorecord__post_init__)
    - [NullableDynamoRecord](#nullabledynamorecord)

## DynamoRecord

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_record.py#L9)

```python
class DynamoRecord(UserDict):
    def __init__(*args: Dict[str, Any], **kwargs: Any) -> None:
```

Dict-based wrapper for DynamoDB records.

#### Examples

```python
@dataclass
class UserRecord(DynamoRecord):
    # required fields
    name: str

    # optional fields
    company: str = "Amazon"
    age: Optional[int] = DynamoRecord.NOT_SET

    def __post_init__(self):
        # do any post-init operations here
        self.age = self.age or 35

record = UserRecord(name="Jon")
record["age"] = 30
record.age = 30
record.update({"age": 30})

record.asdict() # {"name": "Jon", "company": "Amazon", "age": 30}
```

### DynamoRecord().\_\_post\_init\_\_

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_record.py#L59)

```python
def __post_init__() -> None:
```

Override this method for post-init operations

## NullableDynamoRecord

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_record.py#L245)

```python
class NullableDynamoRecord(UserDict):
```

DynamoRecord that allows `None` values
