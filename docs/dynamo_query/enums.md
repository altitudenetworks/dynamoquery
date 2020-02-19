# Enums

> Auto-generated documentation for [dynamo_query.enums](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/enums.py) module.

DynamoDB related enums.

- [dynamo-query](../README.md#dynamo-query) / [Modules](../MODULES.md#dynamo-query-modules) / [Dynamo Query](index.md#dynamo-query) / Enums
    - [ConditionExpressionJoinOperator](#conditionexpressionjoinoperator)
    - [ConditionExpressionOperator](#conditionexpressionoperator)
    - [DynamoQueryType](#dynamoquerytype)
    - [ReturnConsumedCapacity](#returnconsumedcapacity)
    - [ReturnItemCollectionMetrics](#returnitemcollectionmetrics)
    - [ReturnValues](#returnvalues)

## ConditionExpressionJoinOperator

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/enums.py#L123)

```python
class ConditionExpressionJoinOperator(enum.Enum):
```

Enum of operator types that join `ConditionExpression` in a group.

#### Attributes

- `AND` - Rendered as `AND` operator.
- `OR` - Rendered as `OR` operator.

## ConditionExpressionOperator

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/enums.py#L90)

```python
class ConditionExpressionOperator(enum.Enum):
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

## DynamoQueryType

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/enums.py#L18)

```python
class DynamoQueryType(enum.Enum):
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

## ReturnConsumedCapacity

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/enums.py#L43)

```python
class ReturnConsumedCapacity(enum.Enum):
```

Enum of [ReturnConsumedCapacity](#returnconsumedcapacity) argument values for Boto3

#### Attributes

- `INDEXES` - Add indexes only consumed capacity.
- `TOTAL` - Add full consumed capacity.
- `NONE` - Do not add consumed capacity.

## ReturnItemCollectionMetrics

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/enums.py#L77)

```python
class ReturnItemCollectionMetrics(enum.Enum):
```

Enum of [ReturnItemCollectionMetrics](#returnitemcollectionmetrics) argument values for Boto3

#### Attributes

- `NONE` - Do not Include statistics to response.
- `SIZE` - Include size statistics to response.

## ReturnValues

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/enums.py#L58)

```python
class ReturnValues(enum.Enum):
```

Enum of [ReturnValues](#returnvalues) argument values for Boto3

#### Attributes

- `NONE` - Do not return object fields.
- `ALL_OLD` - Return all field values before update operation.
- `UPDATED_OLD` - Return updated field values before update operation.
- `ALL_NEW` - Return all field values as they appear after update operation.
- `UPDATED_NEW` - Return updated field values as they appear after update operation.
