# DynamoQuery changes

- Added `DynamoQuery.table` method that allows to set `Table` and `TableKeys` (breaking!)
- `TableKeys` is always a set
- `ProjectionDict` sorts keys for stable result
- Added `DynamoQuery.limit` method to set limit for query/scan

# DynamoTable changes

- `required_fields` removed, it is user responsibility now (breaking!)
- `get_sort_key` / `get_partition_key` support non-string values
- `create_table` method no longer manages auto-scaling (breaking!)
- `dynamodb_resource.Table` should be passed on construction (breaking!)
- `DataTableError` no longer subclasses `ValueError`

# DynamoTableIndex changes

- Removed `DynamoTableIndex.as_dynamo_dict` method
- Added `DynamoTableIndex.as_global_secondary_index` method
- Added `DynamoTableIndex.as_local_secondary_index` method
- Added `DynamoTableIndex.as_key_schema` method
- Added `DynamoTableIndex.as_attribute_definitions` method

# Expressions changes

- `ConditionExpression` now uses a string operator instead of `enum` (breaking!)
- `ProjectionExpression` sorts keys for stable result
- `ConditionExpression` no longer supports JOIN with strings or tuples
- `ConditionExpressionGroup` no longer supports JOIN with strings or tuples

# Boto3Retrier changes

- No longer shadows argument and return types of a wrapped function
 
# DataTable changes

- Removed partitioning methods
