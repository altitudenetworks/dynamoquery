# DynamoTable

> Auto-generated documentation for [dynamo_query.dynamo_table](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_table.py) module.

- [dynamo-query](../README.md#dynamo-query) / [Modules](../MODULES.md#dynamo-query-modules) / [Dynamo Query](index.md#dynamo-query) / DynamoTable
    - [DynamoTable](#dynamotable)
        - [DynamoTable().batch_delete](#dynamotablebatch_delete)
        - [DynamoTable().batch_get](#dynamotablebatch_get)
        - [DynamoTable().batch_upsert](#dynamotablebatch_upsert)
        - [DynamoTable().clear_table](#dynamotableclear_table)
        - [DynamoTable().create_table](#dynamotablecreate_table)
        - [DynamoTable().delete_record](#dynamotabledelete_record)
        - [DynamoTable().get_partition_key](#dynamotableget_partition_key)
        - [DynamoTable().get_record](#dynamotableget_record)
        - [DynamoTable().get_sort_key](#dynamotableget_sort_key)
        - [DynamoTable().query](#dynamotablequery)
        - [DynamoTable().scan](#dynamotablescan)
        - [DynamoTable().table](#dynamotabletable)
        - [DynamoTable().upsert_record](#dynamotableupsert_record)

## DynamoTable

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_table.py#L32)

```python
class DynamoTable(Generic[DynamoRecord]):
    def __init__(logger: Optional[logging.Logger] = None):
```

### DynamoTable().batch_delete

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_table.py#L233)

```python
def batch_delete(
    data_table: DataTable[DynamoRecord],
) -> DataTable[DynamoRecord]:
```

Delete items by table keys.

`data_table` must have `pk` and `sk` columns with set values.

#### Arguments

- `data_table` - Request data table.

#### Returns

DataTable with deleted records.

### DynamoTable().batch_get

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_table.py#L195)

```python
def batch_get(data_table: DataTable[DynamoRecord]) -> DataTable[DynamoRecord]:
```

Get items by table keys.

`data_table` must have `pk` and `sk` column with set values.

#### Arguments

- `data_table` - Request data table.

#### Returns

DataTable with existing records.

### DynamoTable().batch_upsert

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_table.py#L269)

```python
def batch_upsert(
    data_table: DataTable[DynamoRecord],
) -> DataTable[DynamoRecord]:
```

Upsert DataTable to DB.

#### Arguments

- `data_table` - DataTable with set `pk` and `sk`.

#### Returns

A DataTable with upserted results.

### DynamoTable().clear_table

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_table.py#L135)

```python
def clear_table(partition_key: Optional[str]) -> None:
```

Remove all records.

If `partition_key` is None - deletes all records.

#### Arguments

- `partition_key` - Partition key value.

### DynamoTable().create_table

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_table.py#L89)

```python
def create_table() -> None:
```

### DynamoTable().delete_record

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_table.py#L377)

```python
def delete_record(
    record: DynamoRecord,
    condition_expression: Optional[ConditionExpression] = None,
) -> Optional[DynamoRecord]:
```

Delete Record from DB.

#### Arguments

- `record` - Record with required fields for sort and partition keys.
- `condition_expression` - Condition for delete.

#### Returns

A dict with record data or None.

#### See also

- [DynamoRecord](#dynamorecord)

### DynamoTable().get_partition_key

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_table.py#L77)

```python
def get_partition_key(record: DynamoRecord) -> Any:
```

#### See also

- [DynamoRecord](#dynamorecord)

### DynamoTable().get_record

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_table.py#L310)

```python
def get_record(record: DynamoRecord) -> Optional[DynamoRecord]:
```

Get Record from DB.

#### Arguments

- `record` - Record with required fields for sort and partition keys.

#### Returns

A dict with record data or None.

#### See also

- [DynamoRecord](#dynamorecord)

### DynamoTable().get_sort_key

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_table.py#L83)

```python
def get_sort_key(record: DynamoRecord) -> Any:
```

#### See also

- [DynamoRecord](#dynamorecord)

### DynamoTable().query

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_table.py#L435)

```python
def query(
    partition_key: str,
    index: DynamoTableIndex = primary_index,
    sort_key: Optional[str] = None,
    sort_key_prefix: Optional[str] = None,
    filter_expression: Optional[ConditionExpression] = None,
    scan_index_forward: bool = True,
    projection: Iterable[str] = tuple(),
    data: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None,
) -> Iterator[DynamoRecord]:
```

Yield results from a query using index.

#### Arguments

- `partition_key` - Partition key value.
- `index` - DynamoTableIndex instance, primary index is used if not provided.
- `sort_key` - Sort key value.
- `sort_key_prefix` - Sort key prefix.
- `filter_expression` - Query filter expression.
- `scan_index_forward` - Whether to scan index from the beginning.
- `projection` - Record fields to return, by default returns all fields.
- `limit` - Max number of results.

#### Yields

Matching record.

#### See also

- [DynamoTableIndex](dynamo_table_index.md#dynamotableindex)

### DynamoTable().scan

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_table.py#L407)

```python
def scan(
    filter_expression: Optional[ConditionExpression] = None,
    projection: Iterable[str] = tuple(),
    data: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None,
) -> Iterator[DynamoRecord]:
```

Yield records from a table.

#### Arguments

- `filter_expression` - Query filter expression.
- `scan_index_forward` - Whether to scan index from the beginning.
- `projection` - Record fields to return, by default returns all fields.
- `limit` - Max number of results.

### DynamoTable().table

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_table.py#L52)

```python
@abstractproperty
def table() -> Table:
```

Override this method to get DynamoDB Table resource.

#### See also

- [Table](types.md#table)

### DynamoTable().upsert_record

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_table.py#L338)

```python
def upsert_record(
    record: DynamoRecord,
    condition_expression: Optional[ConditionExpression] = None,
    extra_data: Dict[str, Any] = None,
) -> DynamoRecord:
```

Upsert Record to DB.

#### Arguments

- `record` - Record to insert/update.
- `condition_expression` - Condition for update.
- `extra_data` - Data for query.

#### Returns

A dict with updated record data.

#### See also

- [DynamoRecord](#dynamorecord)
