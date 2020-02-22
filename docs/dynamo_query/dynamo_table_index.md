# DynamoTableIndex

> Auto-generated documentation for [dynamo_query.dynamo_table_index](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table_index.py) module.

- [dynamo-query](../README.md#dynamo-query) / [Modules](../MODULES.md#dynamo-query-modules) / [Dynamo Query](index.md#dynamo-query) / DynamoTableIndex
    - [DynamoTableIndex](#dynamotableindex)
        - [DynamoTableIndex().as_attribute_definitions](#dynamotableindexas_attribute_definitions)
        - [DynamoTableIndex().as_global_secondary_index](#dynamotableindexas_global_secondary_index)
        - [DynamoTableIndex().as_key_schema](#dynamotableindexas_key_schema)
        - [DynamoTableIndex().as_local_secondary_index](#dynamotableindexas_local_secondary_index)
        - [DynamoTableIndex().get_query_data](#dynamotableindexget_query_data)
        - [DynamoTableIndex().name](#dynamotableindexname)

## DynamoTableIndex

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table_index.py#L14)

```python
class DynamoTableIndex():
    def __init__(
        name: str,
        partition_key_name: str,
        sort_key_name: Optional[str],
        partition_key_type: Literal['S', 'N', 'B'] = 'S',
        sort_key_type: Literal['S', 'N', 'B'] = 'S',
    ):
```

Constructor for DynamoDB global and local secondary index structures.

#### Arguments

- `name` - Index name.
- `sort_key` - Sort key attribute name.
- `partition_key` - Partition key attribute name.

Usage:

```python
table_index = DynamoTableIndex("lsi_my_attr", "my_attr")
table_index.as_dynamodb_dict()
# {
#     "IndexName": "lsi_my_attr",
#     "KeySchema": [
#         {"AttributeName": "pk", "KeyType": "HASH",},
#         {"AttributeName": "my_attr", "KeyType": "RANGE"},
#     ],
#     "Projection": {"ProjectionType": "ALL"},
# }

#### Attributes

- `PRIMARY` - Special name for primary table index: `'primary'`

### DynamoTableIndex().as_attribute_definitions

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table_index.py#L124)

```python
def as_attribute_definitions() -> List[ClientCreateTableAttributeDefinitionsTypeDef]:
```

### DynamoTableIndex().as_global_secondary_index

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table_index.py#L65)

```python
def as_global_secondary_index() -> ClientCreateTableGlobalSecondaryIndexesTypeDef:
```

Output a dictionary to use in `dynamo_client.create_table` method.

#### Returns

A dict with index data.

#### See also

- [ClientCreateTableGlobalSecondaryIndexesTypeDef](types.md#clientcreatetableglobalsecondaryindexestypedef)

### DynamoTableIndex().as_key_schema

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table_index.py#L109)

```python
def as_key_schema() -> List[ClientCreateTableKeySchemaTypeDef]:
```

Output a dictionary to use in `dynamo_client.create_table` method.

#### Returns

A dict with index data.

### DynamoTableIndex().as_local_secondary_index

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table_index.py#L87)

```python
def as_local_secondary_index() -> ClientCreateTableLocalSecondaryIndexesTypeDef:
```

Output a dictionary to use in `dynamo_client.create_table` method.

#### Returns

A dict with index data.

#### See also

- [ClientCreateTableLocalSecondaryIndexesTypeDef](types.md#clientcreatetablelocalsecondaryindexestypedef)

### DynamoTableIndex().get_query_data

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table_index.py#L145)

```python
def get_query_data(
    partition_key: str,
    sort_key: Optional[str],
) -> Dict[str, str]:
```

Get query-ready data with `partition_key` and `sort_key` values.

#### Arguments

- `partition_key` - Partition key value.
- `sort_key` - Sort key value.

#### Returns

Query-ready data.

### DynamoTableIndex().name

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/dynamo_table_index.py#L55)

```python
@property
def name() -> Optional[str]:
```

Get index name to use in queries.
