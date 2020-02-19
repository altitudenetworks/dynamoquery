# Base

> Auto-generated documentation for [dynamo_query.base](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/base.py) module.

Helper for building Boto3 DynamoDB queries.

- [dynamo-query](../README.md#dynamo-query) / [Modules](../MODULES.md#dynamo-query-modules) / [Dynamo Query](index.md#dynamo-query) / Base
    - [BaseDynamoQuery](#basedynamoquery)
        - [BaseDynamoQuery().client](#basedynamoqueryclient)
        - [BaseDynamoQuery().has_more_results](#basedynamoqueryhas_more_results)
        - [BaseDynamoQuery().table_keys](#basedynamoquerytable_keys)
        - [BaseDynamoQuery().table_resource](#basedynamoquerytable_resource)
        - [BaseDynamoQuery().was_executed](#basedynamoquerywas_executed)
    - [DynamoQueryError](#dynamoqueryerror)

## BaseDynamoQuery

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/base.py#L41)

```python
class BaseDynamoQuery():
    def __init__(
        query_type: DynamoQueryType,
        expressions: Dict[Text, BaseExpression],
        extra_params: Dict[Text, Any],
        limit: int = MAX_LIMIT,
        exclusive_start_key: Optional[ExclusiveStartKey] = None,
        logger: logging.Logger = None,
    ):
```

Base class for building Boto3 DynamoDB queries. Use
`tools.dynamo_query.dynamo_query.DynamoQuery` instead.

```python
query = BaseDynamoQuery(
    query_type=DynamoQueryType.SCAN,
    expressions={
        BaseDynamoQuery.FILTER_EXPRESSION: ConditionExpression(
            'first_name',
            'last_name,
        ),
    }
    extra_params={}
    limit=5,
)
```

#### Attributes

- `MAX_PAGE_SIZE` - Max size of one scan/query request
- `MAX_BATCH_SIZE` - Max size of one batch_get/write/delete_item request
- `MAX_LIMIT` - Max size of scan/query requests
- `TABLE_KEYS` - Define in a subclass to set table keys automatically.
- `FILTER_EXPRESSION` - Alias for `FilterExpression` parameter name.
- `CONDITION_EXPRESSION` - Alias for `ConditionExpression` parameter name.
- `UPDATE_EXPRESSION` - Alias for `UpdateExpression` parameter name.
- `PROJECTION_EXPRESSION` - Alias for `ProjectionExpression` parameter name.
- `KEY_CONDITION_EXPRESSION` - Alias for `KeyConditionExpression` parameter name.
- `ReturnConsumedCapacity` - Alias for `ReturnConsumedCapacity` enum,

#### Arguments

- `query_type` - DynamoQueryType item.
- `expressions` - Expressions for query.
- `extra_params` - Any exptra params to pass to boto3 method.
- `limit` - Limit of results for scan/query requests.
- `exclusive_start_key` - Start key for scan/query requests.

#### See also

- [DynamoQueryType](enums.md#dynamoquerytype)

### BaseDynamoQuery().client

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/base.py#L134)

```python
@property
def client() -> DynamoDBClient:
```

#### See also

- [DynamoDBClient](types.md#dynamodbclient)

### BaseDynamoQuery().has_more_results

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/base.py#L147)

```python
def has_more_results() -> bool:
```

Whether `scan` or `query` request with `limit` has more results to return.

#### Returns

True if query has more results than returned or was not yet executed.

### BaseDynamoQuery().table_keys

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/base.py#L127)

```python
@property
def table_keys() -> TableKeys:
```

#### See also

- [TableKeys](types.md#tablekeys)

### BaseDynamoQuery().table_resource

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/base.py#L120)

```python
@property
def table_resource() -> Table:
```

#### See also

- [Table](types.md#table)

### BaseDynamoQuery().was_executed

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/base.py#L138)

```python
def was_executed() -> bool:
```

Whether query was excetuted at least once.

#### Returns

True if query was executed.

## DynamoQueryError

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/base.py#L35)

```python
class DynamoQueryError(Exception):
```

Main error for `tools.dynamo_query.dynamo_query.DynamoQuery` class.
