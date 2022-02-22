# Expressions

> Auto-generated documentation for [dynamo_query.expressions](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/expressions.py) module.

Expression builders.

- [dynamo-query](../README.md#dynamoquery) / [Modules](../MODULES.md#dynamo-query-modules) / [Dynamo Query](index.md#dynamo-query) / Expressions
    - [ConditionExpression](#conditionexpression)
        - [ConditionExpression().get_format_keys](#conditionexpressionget_format_keys)
        - [ConditionExpression().get_format_values](#conditionexpressionget_format_values)
        - [ConditionExpression().get_operators](#conditionexpressionget_operators)
    - [ExpressionError](#expressionerror)
    - [ProjectionExpression](#projectionexpression)
        - [ProjectionExpression().get_format_keys](#projectionexpressionget_format_keys)
        - [ProjectionExpression().get_format_values](#projectionexpressionget_format_values)
        - [ProjectionExpression().get_operators](#projectionexpressionget_operators)
    - [UpdateExpression](#updateexpression)
        - [UpdateExpression().get_format_keys](#updateexpressionget_format_keys)
        - [UpdateExpression().get_format_values](#updateexpressionget_format_values)
        - [UpdateExpression().get_operators](#updateexpressionget_operators)
        - [UpdateExpression().validate_input_data](#updateexpressionvalidate_input_data)

## ConditionExpression

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/expressions.py#L250)

```python
class ConditionExpression(BaseConditionExpression):
    def __init__(
        key: str,
        operator: ConditionExpressionOperatorStr = '=',
        value: Any = None,
    ):
```

Part of [ConditionExpression](#conditionexpression).

```python
ConditionExpression(key='name', operator=Operator.IN, value='test').render()
# '{key} IN ({test__value})'
```

#### Arguments

- `key` - Key name.
- `operator` - `ConditionExpressionOperator`
- `value` - Value name to match.

#### See also

- [BaseConditionExpression](#baseconditionexpression)
- [ConditionExpressionOperatorStr](dynamo_query_types.md#conditionexpressionoperatorstr)

### ConditionExpression().get_format_keys

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/expressions.py#L296)

```python
def get_format_keys() -> Set[str]:
```

Get required format keys.

#### Returns

A set of keys.

### ConditionExpression().get_format_values

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/expressions.py#L305)

```python
def get_format_values() -> Set[str]:
```

Get required format values without value postfix.

#### Returns

A set of keys.

### ConditionExpression().get_operators

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/expressions.py#L406)

```python
def get_operators() -> Set[ConditionExpressionOperatorStr]:
```

Get a set of all operators that used in expession group.

## ExpressionError

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/expressions.py#L24)

```python
class ExpressionError(Exception):
```

## ProjectionExpression

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/expressions.py#L176)

```python
class ProjectionExpression(BaseExpression):
    def __init__(*keys: str):
```

Renderer for a format-ready ProjectionExpression.

```python
from dynamo_query.expressions import ProjectionExpression

projection_expression = ProjectionExpression(
    ['first_name', 'last_name']
)
projection_expression.render() # '{first_name}, {last_name}'
```

#### Arguments

- `keys` - Keys to add to expressions.

#### See also

- [BaseExpression](#baseexpression)

### ProjectionExpression().get_format_keys

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/expressions.py#L196)

```python
def get_format_keys() -> Set[str]:
```

Get required format keys.

#### Returns

A set of keys.

### ProjectionExpression().get_format_values

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/expressions.py#L205)

```python
def get_format_values() -> Set[str]:
```

Get required format values without value postfix.

#### Returns

A set of keys.

### ProjectionExpression().get_operators

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/expressions.py#L235)

```python
def get_operators() -> Set[ConditionExpressionOperatorStr]:
```

Get a set of all operators that used in expession group.

## UpdateExpression

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/expressions.py#L536)

```python
class UpdateExpression(BaseExpression):
    def __init__(
        update: Iterable[str] = tuple(),
        set_if_not_exists: Iterable[str] = tuple(),
        add: Iterable[str] = tuple(),
        delete: Iterable[str] = tuple(),
        remove: Iterable[str] = tuple(),
        *args: str,
    ):
```

Renderer for format-ready [UpdateExpression](#updateexpression).

```
update_expression = UpdateExpression(
    update=['first_name'],
    set_if_not_exists=['created_at'],
    add=['tags'],
)
update_expression
# (
#   'SET {first_name} = {first_name__value},'
#   ' {created_at} = if_not_exists({created_at}, {created_at__value})
#   ' ADD {tags} {tags__value}'
# )
```

#### Arguments

- `args` - Keys to use SET expression, use to update values.
- `update` - Keys to use SET expression, use to update values.
- `set_if_not_exists` - Keys to use SET expression, use to add new keys.
- `add` - Keys to use ADD expression, use to extend lists.
- `delete` - Keys to use DELETE expression, use to subtract lists.
- `remove` - Keys to use REMOVE expression, use to remove values.

#### See also

- [BaseExpression](#baseexpression)

### UpdateExpression().get_format_keys

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/expressions.py#L596)

```python
def get_format_keys() -> Set[str]:
```

Get required format keys.

#### Returns

A set of keys.

### UpdateExpression().get_format_values

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/expressions.py#L607)

```python
def get_format_values() -> Set[str]:
```

Get required format values without value postfix.

#### Returns

A set of keys.

### UpdateExpression().get_operators

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/expressions.py#L669)

```python
def get_operators() -> Set[ConditionExpressionOperatorStr]:
```

Get a set of all operators that used in expession group.

### UpdateExpression().validate_input_data

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/expressions.py#L578)

```python
def validate_input_data(data: Dict[(str, Any)]) -> None:
```

Validate data that is used to format the expression.
`ADD` and `DELETE` directives allow only sets and numbers.

#### Arguments

- `data` - Data to validate.

#### Raises

- `ExpressionError` - If data is invalid.
