# DynamoTable

> Auto-generated documentation for [dynamo_query.dynamo_table](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py) module.

- [dynamo-query](../README.md#dynamoquery) / [Modules](../MODULES.md#dynamo-query-modules) / [Dynamo Query](index.md#dynamo-query) / DynamoTable
    - [DynamoTable](#dynamotable)
        - [DynamoTable().batch_delete](#dynamotablebatch_delete)
        - [DynamoTable().batch_delete_records](#dynamotablebatch_delete_records)
        - [DynamoTable().batch_get](#dynamotablebatch_get)
        - [DynamoTable().batch_get_records](#dynamotablebatch_get_records)
        - [DynamoTable().batch_upsert](#dynamotablebatch_upsert)
        - [DynamoTable().batch_upsert_records](#dynamotablebatch_upsert_records)
        - [DynamoTable().clear_table](#dynamotableclear_table)
        - [DynamoTable().client](#dynamotableclient)
        - [DynamoTable().create_table](#dynamotablecreate_table)
        - [DynamoTable().delete_record](#dynamotabledelete_record)
        - [DynamoTable().delete_table](#dynamotabledelete_table)
        - [DynamoTable().get_partition_key](#dynamotableget_partition_key)
        - [DynamoTable().get_record](#dynamotableget_record)
        - [DynamoTable().get_sort_key](#dynamotableget_sort_key)
        - [DynamoTable().max_batch_size](#dynamotablemax_batch_size)
        - [DynamoTable().normalize_record](#dynamotablenormalize_record)
        - [DynamoTable().query](#dynamotablequery)
        - [DynamoTable().scan](#dynamotablescan)
        - [DynamoTable().table](#dynamotabletable)
        - [DynamoTable().upsert_record](#dynamotableupsert_record)
        - [DynamoTable().validate_record_attributes](#dynamotablevalidate_record_attributes)
        - [DynamoTable().wait_until_exists](#dynamotablewait_until_exists)
        - [DynamoTable().wait_until_not_exists](#dynamotablewait_until_not_exists)
    - [DynamoTableError](#dynamotableerror)

## DynamoTable

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L47)

```python
class DynamoTable(Generic[DynamoRecordType], LazyLogger, ABC):
    def __init__(logger: Optional[logging.Logger] = None):
```

DynamoDB table manager, uses `DynamoQuery` underneath.

#### Arguments

- `logger` - `logging.Logger` instance.

#### Examples

```python
from dataclasses import dataclass
from dynamo_query import DynamoTable, DynamoRecord
from typing import Optional

@dataclass
class UserRecord(DynamoRecord):
    pk: str
    email: str
    name: str
    points: Optional[int] = None


# Create your dynamo table manager with your record class
class UserTable(DynamoTable[UserRecord]):
    # provide a set of your table keys
    table_keys = {'pk'}

    # use this property to define your table name
    @property
    def table(self) -> str:
        return "my_table"

    # define how to get PK from a record
    def get_partition_key(self, record: UserRecord) -> str:
        return record.email

    # we do not have a sort key in our table
    def get_sort_key(self, record: UserRecord) -> None:
        return None

    # specify some GSIs
    global_secondary_indexes = [
        DynamoTableIndex("gsi_name", "name", None),
        DynamoTableIndex("gsi_email_age", "email", "age"),
    ]

# and now we can create our table in DynamoDB
user_table = UserTable()
user_table.create_table()
```

#### Attributes

- `partition_key_name` - PK column name: `'pk'`
- `sort_key_name` - SK column name: `'sk'`
- `primary_index` - Primary global index: `DynamoTableIndex(name=DynamoTableIndex.PRIMARY,...`

#### See also

- [LazyLogger](lazy_logger.md#lazylogger)

### DynamoTable().batch_delete

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L395)

```python
def batch_delete(
    data_table: DataTable[DynamoRecordType],
) -> DataTable[DynamoRecordType]:
```

Delete multuple records as a DataTable from DB.

`data_table` must have all columns to calculate table keys.

#### Examples

```python
# UserTable is a subclass of a DynamoTable
user_table = UserTable()

# we should provide table keys or fields to calculate them
# in our case, PK is calculated from `email` field.
users_table = DataTable[UserRecord]().add_record(
    {
        "email": "puppy@gmail.com",
    },
    {
        "email": "elon@gmail.com",
    },
)
deleted_records = user_table.batch_delete(users_table)

for deleted_record in deleted_records:
    # print deleted_record records
    # if record was not found - it will still be returned
    # but only with the data you provided
    print(deleted_record)
```

#### Arguments

- `data_table` - Request data table.

#### Returns

DataTable with deleted records.

### DynamoTable().batch_delete_records

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L548)

```python
def batch_delete_records(
    records: Iterable[DynamoRecordType],
) -> Iterator[DynamoRecordType]:
```

Delete records from DB.

See [DynamoTable().batch_delete](#dynamotablebatch_delete).

#### Arguments

- `records` - Full or partial records to delete.

#### Yields

Deleted or not found record data.

### DynamoTable().batch_get

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L345)

```python
def batch_get(
    data_table: DataTable[DynamoRecordType],
) -> DataTable[DynamoRecordType]:
```

Get multuple records as a DataTable from DB.

`data_table` must have all columns to calculate table keys.

#### Examples

```python
# UserTable is a subclass of a DynamoTable
user_table = UserTable()

# we should provide table keys or fields to calculate them
# in our case, PK is calculated from `email` field.
users_table = DataTable[UserRecord]().add_record(
    {
        "email": "puppy@gmail.com",
    },
    {
        "email": "elon@gmail.com",
    },
)
user_records = user_table.batch_get(users_table)

for user_record in user_records:
    # print found records
    # if record was not found - it will still be returned
    # but only with the data you provided
    print(user_record)
```

#### Arguments

- `data_table` - Request data table.

#### Returns

DataTable with existing records.

### DynamoTable().batch_get_records

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L530)

```python
def batch_get_records(
    records: Iterable[DynamoRecordType],
) -> Iterator[DynamoRecordType]:
```

Get records as an iterator from DB.

See [DynamoTable().batch_get](#dynamotablebatch_get).

#### Arguments

- `records` - Full or partial records data.

#### Yields

Found or not found record data.

### DynamoTable().batch_upsert

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L450)

```python
def batch_upsert(
    data_table: DataTable[DynamoRecordType],
    set_if_not_exists_keys: Iterable[str] = (),
) -> DataTable[DynamoRecordType]:
```

Upsert multuple records as a DataTable to DB.

`data_table` must have all columns to calculate table keys.

Sets `dt_created` field equal to current UTC datetime if a record was created.
Sets `dt_modified` field equal to current UTC datetime.

#### Examples

```python
# UserTable is a subclass of a DynamoTable
user_table = UserTable()

# we should provide table keys or fields to calculate them
# in our case, PK is calculated from `email` field.
users_table = DataTable[UserRecord]().add_record(
    {
        "email": "puppy@gmail.com",
        "name": "Doge Barky",
        "age": 20,
    },
    {
        "email": "elon@gmail.com",
        "name": "Elon Musk",
        "age": 5289,
    },
)
upserted_records = user_table.batch_upsert(users_table)

for upserted_record in upserted_records:
    # print created and updated records
    print(upserted_record)
```

#### Arguments

- `data_table` - Request DataTable.
- `set_if_not_exists_keys` - List of keys to set only if they no do exist in DB.

#### Returns

A DataTable with upserted results.

### DynamoTable().batch_upsert_records

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L568)

```python
def batch_upsert_records(
    records: Iterable[DynamoRecordType],
    set_if_not_exists_keys: Iterable[str] = (),
) -> Iterator[DynamoRecordType]:
```

Upsert records to DB.

See [DynamoTable().batch_upsert](#dynamotablebatch_upsert).

#### Arguments

- `records` - Full or partial records data.
- `set_if_not_exists_keys` - List of keys to set only if they no do exist in DB.

#### Yields

Created, updated or not found record data.

### DynamoTable().clear_table

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L294)

```python
def clear_table(
    partition_key: Optional[str] = None,
    partition_key_prefix: Optional[str] = None,
    sort_key: Optional[str] = None,
    sort_key_prefix: Optional[str] = None,
    index: DynamoTableIndex = primary_index,
    filter_expression: Optional[ConditionExpressionType] = None,
    limit: Optional[int] = None,
) -> None:
```

Remove records from DB.

If `partition_key` and `partition_key_prefix` are None - deletes all records.

#### Arguments

- `partition_key` - Partition key value.
- `sort_key` - Sort key value.
- `partition_key_prefix` - Partition key prefix value.
- `sort_key_prefix` - Sort key prefix value.
- `index` - DynamoTableIndex instance, primary index is used if not provided.
- `filter_expression` - Query filter expression.
- `limit` - Max number of results.

#### See also

- [DynamoTableIndex](dynamo_table_index.md#dynamotableindex)

### DynamoTable().client

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L137)

```python
@property
def client() -> DynamoDBClient:
```

#### See also

- [DynamoDBClient](dynamo_query_types.md#dynamodbclient)

### DynamoTable().create_table

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L185)

```python
def create_table() -> CreateTableOutputTypeDef:
```

Create a table in DynamoDB.

#### Examples

```python
# UserTable is a subclass of a DynamoTable
user_table = UserTable()

# create a table with key schema and all indexes.
UserTable.create_table()
```

#### See also

- [CreateTableOutputTypeDef](dynamo_query_types.md#createtableoutputtypedef)

### DynamoTable().delete_record

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L713)

```python
def delete_record(
    record: DynamoRecordType,
    condition_expression: Optional[ConditionExpression] = None,
) -> Optional[DynamoRecordType]:
```

Delete Record from DB.

`record` must have all fields to calculate table keys.

#### Examples

```python
# UserTable is a subclass of a DynamoTable
user_table = UserTable()

# we should provide table keys or fields to calculate them
# in our case, PK is calculated from `email` field.
deleted_record = user_table.delete_record({
    "email": "cheater@gmail.com",
})

if deleted_record is None:
    # no record found, so nothing was deleted
else:
    # print deleted record
    print(user_record)
```

#### Arguments

- `record` - Record with required fields for sort and partition keys.
- `condition_expression` - Condition for delete.

#### Returns

A dict with record data or None.

#### See also

- [DynamoRecordType](#dynamorecordtype)

### DynamoTable().delete_table

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L169)

```python
def delete_table() -> None:
```

Delete the table from DynamoDB.

#### Examples

```python
# UserTable is a subclass of a DynamoTable
user_table = UserTable()

# delete table
UserTable.delete_table()
```

### DynamoTable().get_partition_key

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L145)

```python
@abstractmethod
def get_partition_key(record: DynamoRecordType) -> Any:
```

Override this method to get PK from a record.

#### See also

- [DynamoRecordType](#dynamorecordtype)

### DynamoTable().get_record

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L591)

```python
def get_record(record: DynamoRecordType) -> Optional[DynamoRecordType]:
```

Get Record from DB.

`record` must have all fields to calculate table keys.

#### Examples

```python
# UserTable is a subclass of a DynamoTable
user_table = UserTable()

# we should provide table keys or fields to calculate them
# in our case, PK is calculated from `email` field.
user_record = user_table.get_record({
    "email": "suspicious@gmail.com",
})

if user_record is None:
    # no record found
    pass
else:
    # print found record
    print(user_record)
```

#### Arguments

- `record` - Record with required fields for sort and partition keys.

#### Returns

A dict with record data or None.

#### See also

- [DynamoRecordType](#dynamorecordtype)

### DynamoTable().get_sort_key

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L151)

```python
@abstractmethod
def get_sort_key(record: DynamoRecordType) -> Any:
```

Override this method to get SK from a record.

#### See also

- [DynamoRecordType](#dynamorecordtype)

### DynamoTable().max_batch_size

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L141)

```python
@property
def max_batch_size() -> int:
```

### DynamoTable().normalize_record

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L241)

```python
def normalize_record(record: DynamoRecordType) -> DynamoRecordType:
```

Modify record before upsert.

#### Arguments

- `record` - Record for upsert.

#### Returns

Normalized record.

#### See also

- [DynamoRecordType](#dynamorecordtype)

### DynamoTable().query

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L815)

```python
def query(
    partition_key: str,
    index: DynamoTableIndex = primary_index,
    sort_key: Optional[str] = None,
    sort_key_prefix: Optional[str] = None,
    filter_expression: Optional[ConditionExpressionType] = None,
    scan_index_forward: bool = True,
    projection: Iterable[str] = tuple(),
    data: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None,
) -> Iterator[DynamoRecordType]:
```

Query table records by index.

#### Examples

```python
# UserTable is a subclass of a DynamoTable
user_table = UserTable()

user_records = user_table.query(
    # query by our PK
    partition_key="new_users",

    # and SK starting with `email_`
    sort_key_prefix="email_",

    # get only users older than ...
    # we will provide values in data
    filter_expression=ConditionExpression("age", "<="),

    # get only first 5 results
    limit=5,

    # get only name and email fields
    projection=("name", "email"),

    # ...older than 45 years
    data= {"age": 45}

    # start with the newest records
    scan_index_forward=False,
)

for user_record in user_records:
    print(user_record)
```

#### Arguments

- `partition_key` - Partition key value.
- `index` - DynamoTableIndex instance, primary index is used if not provided.
- `sort_key` - Sort key value.
- `sort_key_prefix` - Sort key prefix value.
- `filter_expression` - Query filter expression.
- `scan_index_forward` - Whether to scan index from the beginning.
- `projection` - Record fields to return, by default returns all fields.
- `limit` - Max number of results.

#### Yields

Matching record.

#### See also

- [DynamoTableIndex](dynamo_table_index.md#dynamotableindex)

### DynamoTable().scan

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L758)

```python
def scan(
    filter_expression: Optional[ConditionExpressionType] = None,
    projection: Iterable[str] = tuple(),
    data: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None,
) -> Iterator[DynamoRecordType]:
```

List table records.

#### Examples

```python
# UserTable is a subclass of a DynamoTable
user_table = UserTable()

user_records = user_table.scan(
    # get only users older than ...
    # we will provide values in data
    filter_expression=ConditionExpression("age", "<="),

    # get only first 5 results
    limit=5,

    # get only name and email fields
    projection=("name", "email"),

    # ...older than 45 years
    data= {"age": 45}
)

for user_record in user_records:
    print(user_record)
```

#### Arguments

- `filter_expression` - Query filter expression.
- `scan_index_forward` - Whether to scan index from the beginning.
- `projection` - Record fields to return, by default returns all fields.
- `limit` - Max number of results.

### DynamoTable().table

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L131)

```python
@abstractproperty
def table() -> Table:
```

Override this method to get DynamoDB Table resource.

#### See also

- [Table](dynamo_query_types.md#table)

### DynamoTable().upsert_record

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L635)

```python
def upsert_record(
    record: DynamoRecordType,
    condition_expression: Optional[ConditionExpression] = None,
    set_if_not_exists_keys: Iterable[str] = (),
    extra_data: Dict[str, Any] = None,
) -> DynamoRecordType:
```

Upsert Record to DB.

`record` must have all fields to calculate table keys.

Sets `dt_created` field equal to current UTC datetime if a record was created.
Sets `dt_modified` field equal to current UTC datetime.

#### Examples

```python
# UserTable is a subclass of a DynamoTable
user_table = UserTable()

# we should provide table keys or fields to calculate them
# in our case, PK is calculated from `email` field.
user_record = user_table.upsert_record(
    {
        "email": "newuser@gmail.com",
        "name": "Somebody Oncetoldme"
        "age": 23,
    },
    set_if_not_exists_keys=["age"], # set age if it does not exist in DB yet.
)

# print upserted record
print(user_record)
```

#### Arguments

- `record` - Record to insert/update.
- `condition_expression` - Condition for update.
- `set_if_not_exists_keys` - List of keys to set only if they no do exist in DB.
- `extra_data` - Data for query.

#### Returns

A dict with updated record data.

#### See also

- [DynamoRecordType](#dynamorecordtype)

### DynamoTable().validate_record_attributes

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L253)

```python
def validate_record_attributes(record: DynamoRecordType) -> None:
```

Check that all index keys are set correctly in record.

#### Arguments

- `record` - Record for upsert.

#### Raises

- `DynamoTableError` - If index key is missing.

#### See also

- [DynamoRecordType](#dynamorecordtype)

### DynamoTable().wait_until_exists

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L913)

```python
def wait_until_exists() -> None:
```

Proxy method for `resource.Table.wait_until_exists`.

### DynamoTable().wait_until_not_exists

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L919)

```python
def wait_until_not_exists() -> None:
```

Proxy method for `resource.Table.wait_until_not_exists`.

## DynamoTableError

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L27)

```python
class DynamoTableError(BaseException):
    def __init__(message: str, data: Any = None) -> None:
```

Main error for [DynamoTable](#dynamotable) class.

#### Arguments

- `message` - Error message.
- `data` - Addition JSON-serializeable data.
