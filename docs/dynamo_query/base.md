# Base

> Auto-generated documentation for [dynamo_query.base](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/base.py) module.

Helper for building Boto3 DynamoDB queries.

- [dynamo-query](../README.md#dynamoquery) / [Modules](../MODULES.md#dynamo-query-modules) / [Dynamo Query](index.md#dynamo-query) / Base
    - [BaseDynamoQuery](#basedynamoquery)
        - [BaseDynamoQuery().client](#basedynamoqueryclient)
        - [BaseDynamoQuery().has_more_results](#basedynamoqueryhas_more_results)
        - [BaseDynamoQuery().table_keys](#basedynamoquerytable_keys)
        - [BaseDynamoQuery().table_resource](#basedynamoquerytable_resource)
        - [BaseDynamoQuery().was_executed](#basedynamoquerywas_executed)
    - [DynamoQueryError](#dynamoqueryerror)

## BaseDynamoQuery

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/base.py#L41)

```python
class BaseDynamoQuery():
    def __init__(
        query_type: QueryType,
        expressions: Dict[str, BaseExpression],
        extra_params: Dict[str, Any],
        limit: int = MAX_LIMIT,
        exclusive_start_key: Optional[ExclusiveStartKey] = None,
        logger: logging.Logger = None,
    ):
```

Base class for building Boto3 DynamoDB queries. Use
`dynamo_query.DynamoQuery` instead.

```python
query = BaseDynamoQuery(
    query_type=QueryType.SCAN,
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

#### Arguments

- `query_type` - QueryType item.
- `expressions` - Expressions for query.
- `extra_params` - Any exptra params to pass to boto3 method.
- `limit` - Limit of results for scan/query requests.
- `exclusive_start_key` - Start key for scan/query requests.

#### Attributes

- `MAX_PAGE_SIZE` - Max size of one scan/query request.: `1000`
- `MAX_BATCH_SIZE` - Max size of one batch_get/write/delete_item request.: `25`
- `MAX_LIMIT` - Max size of scan/query requests.: `10000000000`

#### See also

- [QueryType](enums.md#querytype)

### BaseDynamoQuery().client

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/base.py#L134)

```python
@property
def client() -> DynamoDBClient:
```

#### See also

- [DynamoDBClient](types.md#dynamodbclient)

### BaseDynamoQuery().has_more_results

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/base.py#L147)

```python
def has_more_results() -> bool:
```

Whether `scan` or `query` request with `limit` has more results to return.

#### Returns

True if query has more results than returned or was not yet executed.

### BaseDynamoQuery().table_keys

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/base.py#L127)

```python
@property
def table_keys() -> TableKeys:
```

#### See also

- [TableKeys](types.md#tablekeys)

### BaseDynamoQuery().table_resource

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/base.py#L120)

```python
@property
def table_resource() -> Table:
```

#### See also

- [Table](types.md#table)

### BaseDynamoQuery().was_executed

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/base.py#L138)

```python
def was_executed() -> bool:
```

Whether query was excetuted at least once.

#### Returns

True if query was executed.

## DynamoQueryError

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/base.py#L35)

```python
class DynamoQueryError(Exception):
```

Main error for [DynamoQuery](dynamo_query.md#dynamoquery) class.
