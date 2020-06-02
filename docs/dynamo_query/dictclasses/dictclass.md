# DictClass

> Auto-generated documentation for [dynamo_query.dictclasses.dictclass](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dictclasses/dictclass.py) module.

- [dynamo-query](../../README.md#dynamoquery) / [Modules](../../MODULES.md#dynamo-query-modules) / [Dynamo Query](../index.md#dynamo-query) / [Dictclasses](index.md#dictclasses) / DictClass
    - [DictClass](#dictclass)
        - [DictClass().\_\_post\_init\_\_](#dictclass__post_init__)
        - [DictClass.compute_key](#dictclasscompute_key)
        - [DictClass().sanitize](#dictclasssanitize)
        - [DictClass.sanitize_key](#dictclasssanitize_key)

## DictClass

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dictclasses/dictclass.py#L14)

```python
class DictClass(UserDict):
    def __init__(*args: Dict[str, Any], **kwargs: Any) -> None:
```

Dict-based dataclass.

#### Examples

```python
class UserRecord(DictClass):
    # required fields
    name: str

    # optional fields
    company: str = "Amazon"
    age: Optional[int] = None

    def __post_init__(self):
        # do any post-init operations here
        self.age = self.age or 35

    # add extra computed field
    @DictClass.compute_key("min_age")
    def _compute_min_age(self) -> int:
        return 18

    # sanitize value on set
    @DictClass.sanitize_key("age")
    def _sanitize_key_age(self, value: int) -> int:
        return max(self.age, 18)

record = UserRecord(name="Jon")
record["age"] = 30
record.age = 30
record.update({"age": 30})

dict(record) # {"name": "Jon", "company": "Amazon", "age": 30, "min_age": 18}
```

### DictClass().\_\_post\_init\_\_

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dictclasses/dictclass.py#L84)

```python
def __post_init__() -> None:
```

Override this method for post-init operations

### DictClass.compute_key

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dictclasses/dictclass.py#L125)

```python
@staticmethod
def compute_key(key: str) -> KeyComputer:
```

#### See also

- [KeyComputer](decorators.md#keycomputer)

### DictClass().sanitize

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dictclasses/dictclass.py#L332)

```python
def sanitize(**kwargs: Any) -> None:
```

Sanitize all set fields.

#### Arguments

- `kwargs` - Arguments for sanitize_key_{key}

### DictClass.sanitize_key

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dictclasses/dictclass.py#L121)

```python
@staticmethod
def sanitize_key(key: str) -> KeySanitizer:
```

#### See also

- [KeySanitizer](decorators.md#keysanitizer)
