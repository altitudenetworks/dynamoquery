# DynamoRecord

> Auto-generated documentation for [dynamo_query.dynamo_record](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_record.py) module.

- [dynamo-query](../README.md#dynamoquery) / [Modules](../MODULES.md#dynamo-query-modules) / [Dynamo Query](index.md#dynamo-query) / DynamoRecord
    - [DynamoRecord](#dynamorecord)
        - [DynamoRecord().asdict](#dynamorecordasdict)
        - [DynamoRecord.fromdict](#dynamorecordfromdict)

## DynamoRecord

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_record.py#L14)

```python
dataclass
class DynamoRecord(UserDict):
```

Dict-based wrapper for DynamoDB records.

#### Examples

```python
@dataclass
class UserRecord(DynamoRecord):
    # required fields
    name: str

    # optional fields
    age: Optional[int] = None

record = UserRecord(name="Jon")
record2 = UserRecord.fromdict({"name": "Jon", "age": 30})
record2["age"] = 30
record2.age = 30
record2.update({"age": 30})

record.asdict() # {"name": "Jon"}
record2.asdict() # {"name": "Jon", "age": 30}
```

#### Attributes

- `NOT_SET` - Indicator that value is not set and should not appear in dict: `None`

### DynamoRecord().asdict

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_record.py#L55)

```python
def asdict() -> Dict[str, Any]:
```

Get dictionary with set values.

#### Examples

```python
UserRecord(name="test").asdict() # {"name": "test"}
UserRecord(name="test", "age": 12).asdict() # {"name": "test", "age": 12}
UserRecord(name="test", age=None) # {"name": "test"}
```

#### Returns

A dictionary.

### DynamoRecord.fromdict

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_record.py#L72)

```python
@classmethod
def fromdict(*mappings: Dict[str, Any]) -> _R:
```

Equivalent of `DynamoRecord(**my_dict)`

#### Arguments

- `mappings` - One or more mappings to extract data.

#### Returns

A new instance.
