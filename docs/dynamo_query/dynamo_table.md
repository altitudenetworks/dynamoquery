# DynamoTable

> Auto-generated documentation for [dynamo_query.dynamo_table](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py) module.

- [dynamo-query](../README.md#dynamoquery) / [Modules](../MODULES.md#dynamo-query-modules) / [Dynamo Query](index.md#dynamo-query) / DynamoTable
    - [DynamoTable](#dynamotable)
        - [DynamoTable().batch_delete](#dynamotablebatch_delete)
        - [DynamoTable().batch_get](#dynamotablebatch_get)
        - [DynamoTable().batch_upsert](#dynamotablebatch_upsert)
        - [DynamoTable().clear_table](#dynamotableclear_table)
        - [DynamoTable().client](#dynamotableclient)
        - [DynamoTable().create_table](#dynamotablecreate_table)
        - [DynamoTable().delete_record](#dynamotabledelete_record)
        - [DynamoTable().delete_table](#dynamotabledelete_table)
        - [DynamoTable().get_partition_key](#dynamotableget_partition_key)
        - [DynamoTable().get_record](#dynamotableget_record)
        - [DynamoTable().get_sort_key](#dynamotableget_sort_key)
        - [DynamoTable().query](#dynamotablequery)
        - [DynamoTable().scan](#dynamotablescan)
        - [DynamoTable().table](#dynamotabletable)
        - [DynamoTable().upsert_record](#dynamotableupsert_record)
    - [DynamoTableError](#dynamotableerror)

## DynamoTable

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L59)

```python
class DynamoTable(Generic[DynamoRecord], LazyLogger):
    def __init__(logger: Optional[logging.Logger] = None):
```

DynamoDB table manager, uses `DynamoQuery` underneath.

#### Arguments

- `logger` - `logging.Logger` instance.

#### Examples

```python
from typing_extensions import TypedDict
from dynamo_query import DynamoTable

# first, define your record
class UserRecord(TypedDict, total=False):
    pk: str
    email: str
    name: str
    points: int


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
        return record["email"]

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

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L387)

```python
def batch_delete(
    data_table: DataTable[DynamoRecord],
) -> DataTable[DynamoRecord]:
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

### DynamoTable().batch_get

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L327)

```python
def batch_get(data_table: DataTable[DynamoRecord]) -> DataTable[DynamoRecord]:
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

### DynamoTable().batch_upsert

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L446)

```python
def batch_upsert(
    data_table: DataTable[DynamoRecord],
    set_if_not_exists_keys: Iterable[str] = (),
) -> DataTable[DynamoRecord]:
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

### DynamoTable().clear_table

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L280)

```python
def clear_table(
    partition_key: Optional[str] = None,
    partition_key_prefix: Optional[str] = None,
    sort_key: Optional[str] = None,
    sort_key_prefix: Optional[str] = None,
    index: DynamoTableIndex = primary_index,
    filter_expression: Optional[ConditionExpression] = None,
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

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L147)

```python
@property
def client() -> DynamoDBClient:
```

#### See also

- [DynamoDBClient](types.md#dynamodbclient)

### DynamoTable().create_table

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L191)

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

- [CreateTableOutputTypeDef](types.md#createtableoutputtypedef)

### DynamoTable().delete_record

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L650)

```python
def delete_record(
    record: DynamoRecord,
    condition_expression: Optional[ConditionExpression] = None,
) -> Optional[DynamoRecord]:
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

- [DynamoRecord](#dynamorecord)

### DynamoTable().delete_table

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L175)

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

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L151)

```python
@abstractmethod
def get_partition_key(record: DynamoRecord) -> Any:
```

Override this method to get PK from a record.

#### See also

- [DynamoRecord](#dynamorecord)

### DynamoTable().get_record

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L529)

```python
def get_record(record: DynamoRecord) -> Optional[DynamoRecord]:
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

- [DynamoRecord](#dynamorecord)

### DynamoTable().get_sort_key

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L157)

```python
@abstractmethod
def get_sort_key(record: DynamoRecord) -> Any:
```

Override this method to get SK from a record.

#### See also

- [DynamoRecord](#dynamorecord)

### DynamoTable().query

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L754)

```python
def query(
    index: DynamoTableIndex = primary_index,
    partition_key: Optional[str] = None,
    partition_key_prefix: Optional[str] = None,
    sort_key: Optional[str] = None,
    sort_key_prefix: Optional[str] = None,
    filter_expression: Optional[ConditionExpression] = None,
    scan_index_forward: bool = True,
    projection: Iterable[str] = tuple(),
    data: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None,
) -> Iterator[DynamoRecord]:
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
- `partition_key_prefix` - Partition key prefix value.
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

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L697)

```python
def scan(
    filter_expression: Optional[ConditionExpression] = None,
    projection: Iterable[str] = tuple(),
    data: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None,
) -> Iterator[DynamoRecord]:
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

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L141)

```python
@abstractproperty
def table() -> Table:
```

Override this method to get DynamoDB Table resource.

#### See also

- [Table](types.md#table)

### DynamoTable().upsert_record

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L575)

```python
def upsert_record(
    record: DynamoRecord,
    condition_expression: Optional[ConditionExpression] = None,
    set_if_not_exists_keys: Iterable[str] = (),
    extra_data: Dict[str, Any] = None,
) -> DynamoRecord:
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

- [DynamoRecord](#dynamorecord)

## DynamoTableError

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table.py#L39)

```python
class DynamoTableError(BaseException):
    def __init__(message: str, data: Any = None) -> None:
```

Main error for [DynamoTable](#dynamotable) class.

#### Arguments

- `message` - Error message.
- `data` - Addition JSON-serializeable data.
