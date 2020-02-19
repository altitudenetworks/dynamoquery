# Expressions

> Auto-generated documentation for [dynamo_query.expressions](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py) module.

- [dynamo-query](../README.md#dynamo-query-index) / [Modules](../MODULES.md#dynamo-query-modules) / [Dynamo Query](index.md#dynamo-query) / Expressions
    - [BaseConditionExpression](#baseconditionexpression)
        - [BaseConditionExpression().get_format_keys](#baseconditionexpressionget_format_keys)
    - [BaseExpression](#baseexpression)
        - [BaseExpression().get_format_keys](#baseexpressionget_format_keys)
        - [BaseExpression().get_format_values](#baseexpressionget_format_values)
        - [BaseExpression().get_operators](#baseexpressionget_operators)
        - [BaseExpression().render](#baseexpressionrender)
        - [BaseExpression().validate_input_data](#baseexpressionvalidate_input_data)
    - [ConditionExpression](#conditionexpression)
        - [ConditionExpression().get_format_keys](#conditionexpressionget_format_keys)
        - [ConditionExpression().get_format_values](#conditionexpressionget_format_values)
        - [ConditionExpression().get_operators](#conditionexpressionget_operators)
    - [ConditionExpressionGroup](#conditionexpressiongroup)
        - [ConditionExpressionGroup().get_format_keys](#conditionexpressiongroupget_format_keys)
        - [ConditionExpressionGroup().get_format_values](#conditionexpressiongroupget_format_values)
        - [ConditionExpressionGroup().get_operators](#conditionexpressiongroupget_operators)
    - [Expression](#expression)
        - [Expression().get_format_keys](#expressionget_format_keys)
        - [Expression().get_format_values](#expressionget_format_values)
        - [Expression().get_operators](#expressionget_operators)
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

## BaseConditionExpression

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L221)

```python
class BaseConditionExpression(BaseExpression):
```

#### See also

- [BaseExpression](#baseexpression)

### BaseConditionExpression().get_format_keys

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L222)

```python
@abstractmethod
def get_format_keys() -> Set[str]:
```

## BaseExpression

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L15)

```python
class BaseExpression():
```

Base class for all expressions. Provides an interface for AWS DynamoDB expression build and
render. Do not use it directly.

### BaseExpression().get_format_keys

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L29)

```python
@abstractmethod
def get_format_keys() -> Set[str]:
```

Get required format keys.

#### Returns

A set of keys.

### BaseExpression().get_format_values

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L39)

```python
@abstractmethod
def get_format_values() -> Set[str]:
```

Get required format values without value postfix.

#### Returns

A set of keys.

### BaseExpression().get_operators

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L61)

```python
@abstractmethod
def get_operators() -> Set[ConditionExpressionOperator]:
```

Get a set of all operators that used in expession group.

### BaseExpression().render

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L77)

```python
def render() -> str:
```

### BaseExpression().validate_input_data

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L49)

```python
def validate_input_data(data: Dict[str, Any]) -> None:
```

Validate data that is used to format the expression.
Override this method in a subclass to add validation logic.

#### Arguments

- `data` - Data to validate.

#### Raises

- `ExpressionError` - If data is invalid.

## ConditionExpression

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L227)

```python
class ConditionExpression(BaseConditionExpression):
    def __init__(
        key: str,
        operator: Union[str, ConditionExpressionOperator] = ConditionExpressionOperator.EQ,
        value: Any = None,
    ):
```

Part of [ConditionExpression](#conditionexpression).

```python
ConditionExpression(key='name', operator=Operator.IN, value='test').render()
# '{key} IN ({test__value})'
```

#### Attributes

- `Operator` - Shortcut for `tools.dynamo_query.expressions.ConditionExpressionOperator`

#### Arguments

- `key` - Key name.
- `operator` - `ConditionExpressionOperator`
- `value` - Value name to match.

#### See also

- [BaseConditionExpression](#baseconditionexpression)

### ConditionExpression().get_format_keys

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L285)

```python
def get_format_keys() -> Set[str]:
```

Get required format keys.

#### Returns

A set of keys.

### ConditionExpression().get_format_values

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L294)

```python
def get_format_values() -> Set[str]:
```

Get required format values without value postfix.

#### Returns

A set of keys.

### ConditionExpression().get_operators

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L428)

```python
def get_operators() -> Set[ConditionExpressionOperator]:
```

Get a set of all operators that used in expession group.

## ConditionExpressionGroup

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L435)

```python
class ConditionExpressionGroup(BaseConditionExpression):
    def __init__(
        expressions: Iterable[ConditionExpression],
        join_operators: Iterable[ConditionExpressionJoinOperator],
    ):
```

Group of [ConditionExpression](#conditionexpression), joins them with OR operator on render.

```python
group = ConditionExpression('key1') & ('key2', ) | ('key3', )

group.render()
# '{key1} = {key1__value}' AND {key2} = {key2__value} OR {key3} = {key3__value}'
```

#### Arguments

- `expressions` - A list of condition expressions to join.

#### See also

- [BaseConditionExpression](#baseconditionexpression)

### ConditionExpressionGroup().get_format_keys

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L458)

```python
def get_format_keys() -> Set[str]:
```

Get required format keys.

#### Returns

A set of keys.

### ConditionExpressionGroup().get_format_values

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L470)

```python
def get_format_values() -> Set[str]:
```

Get required format values without value postfix.

#### Returns

A set of keys.

### ConditionExpressionGroup().get_operators

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L482)

```python
def get_operators() -> Set[ConditionExpressionOperator]:
```

Get a set of all operators that used in expession group.

#### Returns

A set of `ConditionExpressionOperator`.

## Expression

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L89)

```python
class Expression(BaseExpression):
    def __init__(expression_string: str) -> None:
```

Raw expression, use it for for pre-renderer expressions.

```python
expr = Expression('{key} = {key__value}')
expr.render() # '{key} = {key__value}'
```

#### Arguments

- `expression_string` - Format-ready expression string.

#### See also

- [BaseExpression](#baseexpression)

### Expression().get_format_keys

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L111)

```python
def get_format_keys() -> Set[str]:
```

Get required format keys.

#### Returns

A set of keys.

### Expression().get_format_values

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L126)

```python
def get_format_values() -> Set[str]:
```

Get required format values without value postfix.

#### Returns

A set of keys.

### Expression().get_operators

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L150)

```python
def get_operators() -> Set[ConditionExpressionOperator]:
```

Get a set of all operators that used in expession group.

## ExpressionError

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L11)

```python
class ExpressionError(Exception):
```

## ProjectionExpression

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L157)

```python
class ProjectionExpression(BaseExpression):
    def __init__(*keys: str):
```

Renderer for a format-ready ProjectionExpression.

```
projection_expression = DynamoQuery.build_projection_expression(
    ['first_name', 'last_name']
)
projection_expression.render() # '{first_name}, {last_name}'
```

#### Arguments

- `keys` - Keys to add to expressions.

#### See also

- [BaseExpression](#baseexpression)

### ProjectionExpression().get_format_keys

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L175)

```python
def get_format_keys() -> Set[str]:
```

Get required format keys.

#### Returns

A set of keys.

### ProjectionExpression().get_format_values

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L184)

```python
def get_format_values() -> Set[str]:
```

Get required format values without value postfix.

#### Returns

A set of keys.

### ProjectionExpression().get_operators

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L214)

```python
def get_operators() -> Set[ConditionExpressionOperator]:
```

Get a set of all operators that used in expession group.

## UpdateExpression

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L588)

```python
class UpdateExpression(BaseExpression):
    def __init__(
        update: Iterable[str] = tuple(),
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
    add=['tags'],
)
update_expression
# 'SET {first_name} = {first_name__value} ADD {tags} {tags__value}'
```

#### Arguments

- `args` - Keys to use SET expression, use to update values.
- `update` - Keys to use SET expression, use to update values.
- `add` - Keys to use ADD expression, use to extend lists.
- `delete` - Keys to use DELETE expression, use to subtract lists.
- `remove` - Keys to use REMOVE expression, use to remove values.

#### See also

- [BaseExpression](#baseexpression)

### UpdateExpression().get_format_keys

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L644)

```python
def get_format_keys() -> Set[str]:
```

Get required format keys.

#### Returns

A set of keys.

### UpdateExpression().get_format_values

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L655)

```python
def get_format_values() -> Set[str]:
```

Get required format values without value postfix.

#### Returns

A set of keys.

### UpdateExpression().get_operators

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L711)

```python
def get_operators() -> Set[ConditionExpressionOperator]:
```

Get a set of all operators that used in expession group.

### UpdateExpression().validate_input_data

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/expressions.py#L622)

```python
def validate_input_data(data: Dict[str, Any]) -> None:
```

Validate data that is used to format the expression.
`ADD` and `DELETE` directives allow only sets and numbers.

#### Arguments

- `data` - Data to validate.

#### Raises

- `ExpressionError` - If data is invalid.
