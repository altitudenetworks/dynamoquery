# DynamoQuery

> Auto-generated documentation for [dynamo_query.dynamo_query](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_query.py) module.

Helper for building Boto3 DynamoDB queries.

- [dynamo-query](../README.md#dynamo-query) / [Modules](../MODULES.md#dynamo-query-modules) / [Dynamo Query](index.md#dynamo-query) / DynamoQuery
    - [DynamoQuery](#dynamoquery)
        - [DynamoQuery.build_batch_delete_item](#dynamoquerybuild_batch_delete_item)
        - [DynamoQuery.build_batch_get_item](#dynamoquerybuild_batch_get_item)
        - [DynamoQuery.build_batch_update_item](#dynamoquerybuild_batch_update_item)
        - [DynamoQuery.build_delete_item](#dynamoquerybuild_delete_item)
        - [DynamoQuery.build_get_item](#dynamoquerybuild_get_item)
        - [DynamoQuery.build_query](#dynamoquerybuild_query)
        - [DynamoQuery.build_scan](#dynamoquerybuild_scan)
        - [DynamoQuery.build_update_item](#dynamoquerybuild_update_item)
        - [DynamoQuery().execute](#dynamoqueryexecute)
        - [DynamoQuery().execute_dict](#dynamoqueryexecute_dict)
        - [DynamoQuery().get_last_evaluated_key](#dynamoqueryget_last_evaluated_key)
        - [DynamoQuery().get_raw_responses](#dynamoqueryget_raw_responses)
        - [DynamoQuery.get_table_keys](#dynamoqueryget_table_keys)
        - [DynamoQuery().projection](#dynamoqueryprojection)
        - [DynamoQuery().reset_start_key](#dynamoqueryreset_start_key)
        - [DynamoQuery().table](#dynamoquerytable)
        - [DynamoQuery().update](#dynamoqueryupdate)

## DynamoQuery

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_query.py#L32)

```python
class DynamoQuery(BaseDynamoQuery):
```

Helper for building Boto3 DynamoDB queries. See `BaseDynamoQuery`
documentation as well.

```python
query = DynamoQuery.build_scan(
    limit=5,
    filter_expression=ConditionExpression('first_name') & ('last_name', 'in'),
).projection(
    'first_name', 'last_name', 'age',
)
...
data_table = DataTable().add_record({
    'first_name': 'John',
    'last_name': ['Cena', 'Doe', 'Carmack'],
})
table_resource = DynamoConnect().resource.Table('people')
result_data_table = query.execute(
    table_keys=('pk', ),
    table_resource=table_resource,
    data_table=data_table,
)
list(result_data_table.get_records())
# [
#     {
#         'first_name': 'John',
#         'last_name': 'Cena',
#         'age': 42,
#     },
#     {
#         'first_name': 'John',
#         'last_name': 'Carmack',
#         'age': 49,
#     }
# ]
```

#### Attributes

- `MAX_LIMIT` - Max size of scan/query requests
- `TABLE_KEYS` - Define in a subclass to set table keys automatically.

#### See also

- [BaseDynamoQuery](base.md#basedynamoquery)

### DynamoQuery.build_batch_delete_item

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_query.py#L466)

```python
@classmethod
def build_batch_delete_item(
    return_consumed_capacity: ReturnConsumedCapacity = 'NONE',
    return_item_collection_metrics: ReturnItemCollectionMetrics = 'NONE',
) -> 'DynamoQuery':
```

Build delete query for `table.meta.client.batch_write_item`.

```python
query = DynamoQuery.build_batch_delete_item()
data_table = DataTable().add_record({
    'pk': 'key1',
}, {
    'pk': 'key2',
})

result_data_table = query.execute(
    table_resource=boto3_resource.Table('my_table'),
    table_keys=['pk'],
    data_table=data_table,
)
```

#### Arguments

- `return_consumed_capacity` - `ReturnConsumedCapacity` value.
- `return_item_collection_metrics` - `ReturnItemCollectionMetrics` value.

#### Returns

[DynamoQuery](#dynamoquery) instance to execute.

#### See also

- [ReturnConsumedCapacity](types.md#returnconsumedcapacity)
- [ReturnItemCollectionMetrics](types.md#returnitemcollectionmetrics)

### DynamoQuery.build_batch_get_item

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_query.py#L388)

```python
@classmethod
def build_batch_get_item(
    return_consumed_capacity: ReturnConsumedCapacity = 'NONE',
) -> 'DynamoQuery':
```

Build query for `table.meta.client.batch_get_item`.

```python
query = DynamoQuery.build_batch_get_item()
data_table = DataTable().add_record({
    'pk': 'key1',
}, {
    'pk': 'key2',
})

result_data_table = query.execute(
    table_resource=boto3_resource.Table('my_table'),
    table_keys=['pk'],
    data_table=data_table,
)
```

#### Arguments

- `return_consumed_capacity` - `ReturnConsumedCapacity` value.

#### Returns

[DynamoQuery](#dynamoquery) instance to execute.

#### See also

- [ReturnConsumedCapacity](types.md#returnconsumedcapacity)

### DynamoQuery.build_batch_update_item

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_query.py#L423)

```python
@classmethod
def build_batch_update_item(
    return_consumed_capacity: ReturnConsumedCapacity = 'NONE',
    return_item_collection_metrics: ReturnItemCollectionMetrics = 'NONE',
) -> 'DynamoQuery':
```

Build update query for `table.meta.client.batch_write_item`.

```python
query = DynamoQuery.build_batch_update_item()
data_table = DataTable().add_record({
    'pk': 'key1',
    'first_name': 'John',
}, {
    'pk': 'key2',
    'first_name': 'Smith',
})

result_data_table = query.execute(
    table_resource=boto3_resource.Table('my_table'),
    table_keys=['pk'],
    data_table=data_table,
)
```

#### Arguments

- `return_consumed_capacity` - `ReturnConsumedCapacity` value.
- `return_item_collection_metrics` - `ReturnItemCollectionMetrics` value.

#### Returns

[DynamoQuery](#dynamoquery) instance to execute.

#### See also

- [ReturnConsumedCapacity](types.md#returnconsumedcapacity)
- [ReturnItemCollectionMetrics](types.md#returnitemcollectionmetrics)

### DynamoQuery.build_delete_item

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_query.py#L332)

```python
@classmethod
def build_delete_item(
    condition_expression: Optional[BaseConditionExpression] = None,
    return_consumed_capacity: ReturnConsumedCapacity = 'NONE',
    return_item_collection_metrics: ReturnItemCollectionMetrics = 'NONE',
    return_values: ReturnValues = 'ALL_OLD',
) -> 'DynamoQuery':
```

Build query for `table.delete_item`.

```python
query = DynamoQuery.build_delete_item(
    filter_expression=ConditionExpression('first_name')
)

data_table = DataTable().add_record({
    'pk': 'key1',
    'first_name': 'John',
}, {
    'pk': 'key2',
    'first_name': 'Mike',
})

result_data_table = query.execute(
    table_resource=boto3_resource.Table('my_table'),
    table_keys=['pk'],
    data_table=data_table,
)
```

#### Arguments

- `condition_expression` - Format-ready ConditionExpression.
- `return_consumed_capacity` - `ReturnConsumedCapacity` value.
- `return_item_collection_metrics` - `ReturnItemCollectionMetrics` value.
- `return_values` - `ReturnValues` value.

#### Returns

[DynamoQuery](#dynamoquery) instance to execute.

#### See also

- [ReturnConsumedCapacity](types.md#returnconsumedcapacity)
- [ReturnItemCollectionMetrics](types.md#returnitemcollectionmetrics)
- [ReturnValues](types.md#returnvalues)

### DynamoQuery.build_get_item

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_query.py#L215)

```python
@classmethod
def build_get_item(
    projection_expression: Optional[ProjectionExpression] = None,
    consistent_read: bool = False,
    return_consumed_capacity: ReturnConsumedCapacity = 'NONE',
) -> 'DynamoQuery':
```

Build query for `table.get_item`.

```python
query = DynamoQuery.build_get_item().projection(
    'first_name', 'last_name', 'age'
)

data_table = DataTable().add_record({
    'pk': 'key1',
}, {
    'pk': 'key2',
})

result_data_table = query.execute(
    table_resource=boto3_resource.Table('my_table'),
    table_keys=['pk'],
    data_table=data_table,
)
```

#### Arguments

- `projection_expression` - Format-ready ProjectionExpression.
- `consistent_read` - `ConsistentRead` boto3 parameter.
- `return_consumed_capacity` - `ReturnConsumedCapacity` value.

#### Returns

[DynamoQuery](#dynamoquery) instance to execute.

#### See also

- [ReturnConsumedCapacity](types.md#returnconsumedcapacity)

### DynamoQuery.build_query

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_query.py#L78)

```python
@classmethod
def build_query(
    key_condition_expression: BaseConditionExpression,
    index_name: Optional[Text] = None,
    projection_expression: Optional[ProjectionExpression] = None,
    filter_expression: Optional[BaseConditionExpression] = None,
    limit: int = MAX_LIMIT,
    exclusive_start_key: Optional[ExclusiveStartKey] = None,
    consistent_read: bool = False,
    scan_index_forward: bool = True,
) -> 'DynamoQuery':
```

Build query for `table.query`.

```python
query = DynamoQuery.build_query(
    key_condition_expression=ConditionExpression('first_name'),
    filter_expression=ConditionExpression('last_name', 'in'),
    index_name='gsi_first_name',
    limit=5,
    exclusive_start_key={'pk': '1'},
).projection(
    'first_name', 'last_name', 'age'
)

data_table = DataTable().add_record({
    'first_name': 'Test',
    'last_name': ['Last', 'Last2'],
}, {
    'first_name': 'John',
    'last_name': ['Last', 'Last2'],
})

result_data_table = query.execute(
    table_resource=boto3_resource.Table('my_table'),
    table_keys=['pk'],
    data_table=data_table,
)
```

#### Arguments

- `key_condition_expression` - Format-ready KeyConditionExpression.
- `filter_expression` - Format-ready FilterExpression.
- `projection_expression` - Format-ready ProjectionExpression.
- `limit` - Maximum number of results per input record.
- `exclusive_start_key` - Key to start scan from.
- `consistent_read` - `ConsistentRead` boto3 parameter.
- `scan_index_forward` - Whether to scan index from the beginning.

#### Returns

[DynamoQuery](#dynamoquery) instance to execute.

#### See also

- [BaseConditionExpression](expressions.md#baseconditionexpression)

### DynamoQuery.build_scan

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_query.py#L153)

```python
@classmethod
def build_scan(
    filter_expression: Optional[BaseConditionExpression] = None,
    projection_expression: Optional[ProjectionExpression] = None,
    limit: int = MAX_LIMIT,
    exclusive_start_key: Optional[ExclusiveStartKey] = None,
) -> 'DynamoQuery':
```

Build query for `table.scan`.

If `filter_expression` is not provided - it is constructed from input data.

```python
query = DynamoQuery.build_scan(
    filter_expression=ConditionExpression('first_name') & ('last_name', 'in')
    limit=5,
    exclusive_start_key={'pk': '1'}
).projection(
    'first_name', 'last_name', 'age'
)

data_table = DataTable().add_record({
    'first_name': 'Test',
    'last_name': ['Last', 'Last2'],
}, {
    'first_name': 'John',
    'last_name': ['Last', 'Last2'],
})

result_data_table = query.execute(
    table_resource=boto3_resource.Table('my_table'),
    table_keys=['pk'],
    data_table=data_table,
)
```

#### Arguments

- `filter_expression` - Format-ready FilterExpression.
- `projection_expression` - Format-ready ProjectionExpression.
- `limit` - Maximum number of results per input record.
- `exclusive_start_key` - Key to start scan from.

#### Returns

[DynamoQuery](#dynamoquery) instance to execute.

### DynamoQuery.build_update_item

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_query.py#L266)

```python
@classmethod
def build_update_item(
    condition_expression: Optional[BaseConditionExpression] = None,
    update_expression: Optional[UpdateExpression] = None,
    return_consumed_capacity: ReturnConsumedCapacity = 'NONE',
    return_item_collection_metrics: ReturnItemCollectionMetrics = 'NONE',
    return_values: ReturnValues = 'ALL_NEW',
) -> 'DynamoQuery':
```

Build query for `table.update_item`.

If `update_expression` is not provided - it is constructed from input data.

```python
query = DynamoQuery.build_update_item(
    filter_expression=ConditionExpression('first_name')
).update(
    'last_name', 'age',
)

data_table = DataTable().add_record({
    'pk': 'key1',
    'first_name': 'John',
    'age': 32,
}, {
    'pk': 'key2',
    'first_name': 'Mike',
    'age': 19,
})

result_data_table = query.execute(
    table_resource=boto3_resource.Table('my_table'),
    table_keys=['pk'],
    data_table=data_table,
)
```

#### Arguments

- `condition_expression` - Format-ready ConditionExpression.
- `update_expression` - Format-ready UpdateExpression.
- `return_consumed_capacity` - `ReturnConsumedCapacity` value.
- `return_item_collection_metrics` - `ReturnItemCollectionMetrics` value.
- `return_values` - `ReturnValues` value.

#### Returns

[DynamoQuery](#dynamoquery) instance to execute.

#### See also

- [ReturnConsumedCapacity](types.md#returnconsumedcapacity)
- [ReturnItemCollectionMetrics](types.md#returnitemcollectionmetrics)
- [ReturnValues](types.md#returnvalues)

### DynamoQuery().execute

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_query.py#L521)

```python
def execute(
    data_table: DataTable,
    table: Optional[Table] = None,
    table_keys: Optional[TableKeys] = TABLE_KEYS,
) -> DataTable:
```

Execute a query and get results. To get raw AWS responses, use
`query.get_raw_responses()` after this method. To get `LastEvaluatedKey`, use
`query.get_last_evaluated_key()` after this method.

If `table_keys` were not provided, method gets them from table schema. It is
slow, so it is better to pass them explicitly.

```python
input_data_table = DataTable()
input_data_table.add_record({
    'name': 'John',
}, {
    'name': 'Mike',
})
results = DynamoQuery.build_scan(
    filter_expression=ConditionExpression('name'),
).execute(
    table_keys=['pk'],
    table=table_resource,
    data_table=input_data_table,
)
```

#### Arguments

- `table` - `boto3_resource.Table('my_table')`.
- `data_table` - `DataTable` with input data.
- `table_keys` - Primary and sort keys for table.

#### Returns

A `DataTable` with query results.

#### See also

- [DataTable](data_table.md#datatable)

### DynamoQuery().execute_dict

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_query.py#L593)

```python
def execute_dict(
    data: Dict[Text, Any],
    table: Optional[Table] = None,
    table_keys: Optional[TableKeys] = TABLE_KEYS,
) -> DataTable:
```

Execute a query for a single record and get results. See [DynamoQuery().execute](#dynamoqueryexecute) method.

```python
search_data = {
    'name': 'John',
}
results = DynamoQuery.build_scan(
    filter_expression=ConditionExpression('name'),
).execute_dict(
    table_keys=['pk'],
    table=table_resource,
    data=search_data,
)
```

#### Arguments

- `table` - `boto3_resource.Table('my_table')`.
- `data` - Record of a `DataTable` or a regular `dict`.
- `table_keys` - Primary and sort keys for table.

#### Returns

A `DataTable` with query results.

#### See also

- [DataTable](data_table.md#datatable)

### DynamoQuery().get_last_evaluated_key

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_query.py#L630)

```python
def get_last_evaluated_key() -> Optional[ExclusiveStartKey]:
```

Get LastEvaluatedKey from the last execution.

```python
query = DynamoQuery.build_scan(limit=5)
results = query.execute()

# if you use the same query it remembers LastEvaluatedKey, so you get the next page
# on the next execution

results_page2 = query.execute()

# to continue from the same place later, save `LastEvaluatedKey`

start_key = query.get_last_evaluated_key()

query2 = DynamoQuery.build_scan(
    limit=5,
    exclusive_start_key=start_key,
)
results_page3 = query.execute()
```

#### Returns

A dict that can be used in `ExclusiveStartKey` parameter.

### DynamoQuery().get_raw_responses

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_query.py#L666)

```python
def get_raw_responses() -> List[Dict]:
```

Get raw AWS responses from the last execution. Use flags `ReturnConsumedCapacity` and
`ReturnItemCollectionMetrics` to get additional metrics. Also `Count` and `ScannedCount`
fields might be interesting.

#### Returns

A list of AWS responses.

### DynamoQuery.get_table_keys

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_query.py#L677)

```python
@staticmethod
def get_table_keys(table: Table) -> List[Text]:
```

Get table keys from schema.

```python
table = boto3.resource('dynamodb').Table('my_table')
table_keys = DynamoQuery.get_table_keys()
table_keys # ['pk', 'sk']
```

#### Arguments

- `table` - `boto3_resource.Table('my_table')`.

#### Returns

A list of table keys.

#### See also

- [Table](types.md#table)

### DynamoQuery().projection

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_query.py#L702)

```python
def projection(*fields: Text) -> 'DynamoQuery':
```

Django ORM-like shortcut for adding `ProjectionExpression`

```python
query = DynamoQuery.build_update()
query.projection(update=['field1', 'field2')

# lines above are equivalent to

query = DynamoQuery.build_update(
    projection_expression=ProjectionExpression('field1', 'field2')
)
```

#### Arguments

fields - A list of fields to use as ProjectionExpression keys

#### Returns

Itself, so this method can be chained.

### DynamoQuery().reset_start_key

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_query.py#L659)

```python
def reset_start_key() -> 'DynamoQuery':
```

Set paginated query to the start.

### DynamoQuery().table

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_query.py#L507)

```python
def table(
    table: Optional[Table],
    table_keys: Optional[TableKeys] = TABLE_KEYS,
) -> 'DynamoQuery':
```

Set table resource and table keys.

#### Arguments

- `table` - `boto3_resource.Table('my_table')`.
- `table_keys` - Primary and sort keys for table.

### DynamoQuery().update

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/dynamo_query.py#L732)

```python
def update(
    update: Iterable[Text] = tuple(),
    add: Iterable[Text] = tuple(),
    delete: Iterable[Text] = tuple(),
    remove: Iterable[Text] = tuple(),
    *args: Text,
) -> 'DynamoQuery':
```

Shortcut for adding `UpdateExpression`.

```python
query = DynamoQuery.build_update()
query.update(update=['field1'], add=['my_list'])

# lines above are equivalent to

query = DynamoQuery.build_update(
    update_expression=UpdateExpression(update=['field1'], add=['my_list'])
)
```

#### Arguments

- `args` - Keys to use SET expression, use to update values.
- `update` - Keys to use SET expression, use to update values.
- `add` - Keys to use ADD expression, use to extend lists.
- `delete` - Keys to use DELETE expression, use to subtract lists.
- `remove` - Keys to use REMOVE expression, use to remove values.

#### Returns

Itself, so this method can be chained.
