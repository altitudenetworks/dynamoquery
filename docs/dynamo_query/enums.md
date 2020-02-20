# Enums

> Auto-generated documentation for [dynamo_query.enums](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/enums.py) module.

DynamoDB related enums.

- [dynamo-query](../README.md#dynamo-query) / [Modules](../MODULES.md#dynamo-query-modules) / [Dynamo Query](index.md#dynamo-query) / Enums
    - [Operator](#operator)
        - [Operator.values](#operatorvalues)
    - [QueryType](#querytype)

## Operator

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/enums.py#L40)

```python
class Operator(enum.Enum):
```

Enum of operator types that can be used as postfixes in `ConditionExpression` keys.

#### Attributes

- `EQ` - Rendered as `=` operator.
- `NE` - Rendered as `<>` operator.
- `IN` - Rendered as `IN` operator.
- `GT` - Rendered as `>` operator.
- `LT` - Rendered as `<` operator.
- `GTE` - Rendered as `>=` operator.
- `LTE` - Rendered as `<=` operator.
- `BEGINS_WITH` - Rendered as `begins_with(<key>, <value>)` function.
- `EXISTS` - Rendered as `attribute_exists(<key>)` function.
- `NOT_EXISTS` - Rendered as `attribute_not_exists(<key>)` function.
- `BETWEEN` - Rendered as `BETWEEN <value1> AND <value2>` operator.
- `CONTAINS` - Rendered as `contains(<key>, <value>)` function.

### Operator.values

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/enums.py#L72)

```python
@classmethod
def values() -> Set[str]:
```

## QueryType

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/enums.py#L15)

```python
class QueryType(enum.Enum):
```

Enum of DynamoQuery query types.

#### Attributes

- `QUERY` - Used by DynamoQuery.build_query method
- `SCAN` - Used by DynamoQuery.build_scan method
- `GET_ITEM` - Used by DynamoQuery.build_get_item method
- `UPDATE_ITEM` - Used by DynamoQuery.build_update_item method
- `DELETE_ITEM` - Used by DynamoQuery.build_delete_item method
- `BATCH_GET_ITEM` - Used by DynamoQuery.build_batch_get_item method
- `BATCH_UPDATE_ITEM` - Used by DynamoQuery.build_batch_update_item method
- `BATCH_DELETE_ITEM` - Used by DynamoQuery.build_batch_delete_item method
