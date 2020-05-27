"""
Expression builders.
"""
from abc import abstractmethod
from typing import Any, Dict, Iterable, List, Set, Tuple, TypeVar, Union

from dynamo_query.dynamo_query_types import (
    ConditionExpressionJoinOperatorStr,
    ConditionExpressionOperatorStr,
)
from dynamo_query.enums import Operator
from dynamo_query.utils import get_format_keys

__all__ = (
    "ExpressionError",
    "ProjectionExpression",
    "UpdateExpression",
    "ConditionExpression",
)


ExpressionType = TypeVar("ExpressionType", bound="Expression")
ProjectionExpressionType = TypeVar("ProjectionExpressionType", bound="ProjectionExpression")
UpdateExpressionType = TypeVar("UpdateExpressionType", bound="UpdateExpression")


class ExpressionError(Exception):
    pass


class BaseExpression:
    """
    Base class for all expressions. Provides an interface for AWS DynamoDB expression build and
    render. Do not use it directly.
    """

    _value_key_postfix = "__value"

    def __str__(self) -> str:
        return self.render()

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} "{self._render()}">'

    @abstractmethod
    def get_format_keys(self) -> Set[str]:
        """
        Get required format keys.

        Returns:
            A set of keys.
        """

    @abstractmethod
    def get_format_values(self) -> Set[str]:
        """
        Get required format values without value postfix.

        Returns:
            A set of keys.
        """

    def validate_input_data(self, data: Dict[str, Any]) -> None:
        """
        Validate data that is used to format the expression.
        Override this method in a subclass to add validation logic.

        Arguments:
            data -- Data to validate.

        Raises:
            ExpressionError -- If data is invalid.
        """

    @abstractmethod
    def get_operators(self) -> Set[ConditionExpressionOperatorStr]:
        """
        Get a set of all operators that used in expession group.
        """

    @staticmethod
    def _extend_lists_dedup(*lists: Iterable[Any]) -> List[Any]:
        result: List[Any] = []
        for extend_list in lists:
            for item in extend_list:
                if item not in result:
                    result.append(item)

        return result

    def render(self) -> str:
        result = self._render()
        if not result:
            raise ExpressionError(f"{repr(self)} cannot be empty")

        return result

    @abstractmethod
    def _render(self) -> str:
        """
        Render expression to a string.
        """


class Expression(BaseExpression):
    """
    Raw expression, use it for for pre-renderer expressions.

    ```python
    expr = Expression('{key} = {key__value}')
    expr.render() # '{key} = {key__value}'
    ```

    Arguments:
        expression_string -- Format-ready expression string.
    """

    def __init__(self, expression_string: str) -> None:
        self.data = expression_string

    def __or__(self: ExpressionType, other: ExpressionType) -> ExpressionType:
        if isinstance(other, Expression):
            return self.__class__(f"{self.render()} OR {other.render()}")

        raise ExpressionError(f"Incompatible expression operation: {self.render()} AND {other}")

    def __and__(self: ExpressionType, other: ExpressionType) -> ExpressionType:
        if isinstance(other, Expression):
            return self.__class__(f"{self.render()} AND {other.render()}")

        raise ExpressionError(f"Incompatible expression operation: {self.render()} AND {other}")

    def get_format_keys(self) -> Set[str]:
        """
        Get required format keys.

        Returns:
            A set of keys.
        """
        keys = get_format_keys(self.data)
        result = set()
        for key in keys:
            if not key.endswith(self._value_key_postfix):
                result.add(key)

        return result

    def get_format_values(self) -> Set[str]:
        """
        Get required format values without value postfix.

        Returns:
            A set of keys.
        """
        keys = get_format_keys(self.data)
        result = set()
        for key in keys:
            if key.endswith(self._value_key_postfix):
                result.add(key.replace(self._value_key_postfix, ""))

        return result

    def _render(self) -> str:
        """
        Render expression to string. Override this method in a subclass.

        Returns:
            A rendered expression as a string.
        """
        return self.data

    def get_operators(self) -> Set[ConditionExpressionOperatorStr]:
        """
        Get a set of all operators that used in expession group.
        """
        return set()


class ProjectionExpression(BaseExpression):
    """
    Renderer for a format-ready ProjectionExpression.

    ```
    projection_expression = DynamoQuery.build_projection_expression(
        ['first_name', 'last_name']
    )
    projection_expression.render() # '{first_name}, {last_name}'
    ```

    Arguments:
        keys -- Keys to add to expressions.
    """

    def __init__(self, *keys: str):
        self.keys: Tuple[str, ...] = tuple(sorted(keys))

    def get_format_keys(self) -> Set[str]:
        """
        Get required format keys.

        Returns:
            A set of keys.
        """
        return set(self.keys)

    def get_format_values(self) -> Set[str]:
        """
        Get required format values without value postfix.

        Returns:
            A set of keys.
        """
        return set()

    def __and__(
        self: ProjectionExpressionType, other: ProjectionExpressionType
    ) -> ProjectionExpressionType:
        if isinstance(other, ProjectionExpression):
            return self.__class__(*self._extend_lists_dedup(self.keys, other.keys))

        raise ExpressionError(f"Incompatible expression operation: {self.render()} AND {other}")

    def _render(self) -> str:
        """
        Render expression to string.

        Returns:
            A rendered expression as a string.
        """
        key_list = []
        for key in self.keys:
            key_list.append(f"{{{key}}}")

        return ", ".join(key_list)

    def get_operators(self) -> Set[ConditionExpressionOperatorStr]:
        """
        Get a set of all operators that used in expession group.
        """
        return set()


class BaseConditionExpression(BaseExpression):
    @abstractmethod
    def get_format_keys(self) -> Set[str]:
        """
        Get required format keys.
        """


class ConditionExpression(BaseConditionExpression):
    """
    Part of `ConditionExpression`.

    ```python
    ConditionExpression(key='name', operator=Operator.IN, value='test').render()
    # '{key} IN ({test__value})'
    ```

    Arguments:
        key -- Key name.
        operator -- `ConditionExpressionOperator`
        value -- Value name to match.
    """

    _value_key_postfix = "__value"

    def __init__(
        self, key: str, operator: ConditionExpressionOperatorStr = "=", value: Any = None,
    ):
        try:
            Operator(operator)
        except ValueError:
            raise ExpressionError(f"Invalid operator {operator}, choices are {Operator.values()}")

        if operator == "BETWEEN":
            if not isinstance(value, (list, tuple)) or len(value) != 2:
                raise ExpressionError(
                    f"Operator BETWEEN requires a list of two values, got {value}."
                )

        if value is None:
            if operator in ("attribute_exists", "attribute_not_exists"):
                value = True
            else:
                value = key

        self.key = key
        self.operator = operator
        self.value: Any = value

    def get_format_keys(self) -> Set[str]:
        """
        Get required format keys.

        Returns:
            A set of keys.
        """
        return {self.key}

    def get_format_values(self) -> Set[str]:
        """
        Get required format values without value postfix.

        Returns:
            A set of keys.
        """
        if self.operator in ("attribute_exists", "attribute_not_exists"):
            return set()
        if self.operator == "BETWEEN":
            return {self.value[0], self.value[1]}

        return {self.value}

    def __or__(
        self, other: Union["ConditionExpression", "ConditionExpressionGroup"],
    ) -> "ConditionExpressionGroup":
        join_operators: List[ConditionExpressionJoinOperatorStr] = []
        if isinstance(other, ConditionExpressionGroup):
            join_operators.append("OR")
            join_operators.extend(other.join_operators)
            expressions = []
            expressions.append(self)
            expressions.extend(other.expressions)
            return ConditionExpressionGroup(expressions=expressions, join_operators=join_operators)

        if isinstance(other, ConditionExpression):
            join_operators.append("OR")
            return ConditionExpressionGroup(
                expressions=[self, other], join_operators=join_operators
            )

        raise ExpressionError(f"Incompatible expression operation: {self.render()} AND {other}")

    def __and__(
        self, other: Union["ConditionExpression", "ConditionExpressionGroup"],
    ) -> "ConditionExpressionGroup":
        join_operators: List[ConditionExpressionJoinOperatorStr] = []
        if isinstance(other, ConditionExpressionGroup):
            join_operators.append("AND")
            join_operators.extend(other.join_operators)
            expressions = []
            expressions.append(self)
            expressions.extend(other.expressions)
            return ConditionExpressionGroup(expressions=expressions, join_operators=join_operators)

        if isinstance(other, ConditionExpression):
            join_operators.append("AND")
            return ConditionExpressionGroup(
                expressions=[self, other], join_operators=join_operators
            )

        raise ExpressionError(f"Incompatible expression operation: {self.render()} AND {other}")

    def _render(self) -> str:
        """
        Render expression part to string.

        Returns:
            A rendered expression part as a string.
        """
        if self.operator == "IN":
            return f"{{{self.key}}} IN ({{{self.value}{self._value_key_postfix}}})"

        if self.operator == "BETWEEN":
            return (
                f"{{{self.key}}} BETWEEN {{{self.value[0]}{self._value_key_postfix}}}"
                f" AND {{{self.value[1]}{self._value_key_postfix}}}"
            )

        if self.operator == "begins_with":
            return f"begins_with({{{self.key}}}, {{{self.value}{self._value_key_postfix}}})"

        if self.operator == "contains":
            return f"contains({{{self.key}}}, {{{self.value}{self._value_key_postfix}}})"

        if self.operator == "attribute_exists":
            function_name = "attribute_exists"
            if not self.value:
                function_name = "attribute_not_exists"

            return f"{function_name}({{{self.key}}})"

        if self.operator == "attribute_not_exists":
            function_name = "attribute_not_exists"
            if not self.value:
                function_name = "attribute_exists"

            return f"{function_name}({{{self.key}}})"

        return f"{{{self.key}}} {self.operator} {{{self.value}{self._value_key_postfix}}}"

    def get_operators(self) -> Set[ConditionExpressionOperatorStr]:
        """
        Get a set of all operators that used in expession group.
        """
        return {self.operator}


class ConditionExpressionGroup(BaseConditionExpression):
    """
    Group of `ConditionExpression`, joins them with OR operator on render.

    ```python
    group = ConditionExpression('key1') & ('key2', ) | ('key3', )

    group.render()
    # '{key1} = {key1__value}' AND {key2} = {key2__value} OR {key3} = {key3__value}'
    ```

    Arguments:
        expressions -- A list of condition expressions to join.
    """

    def __init__(
        self,
        expressions: Iterable[ConditionExpression],
        join_operators: Iterable[ConditionExpressionJoinOperatorStr],
    ):
        self.expressions = tuple(expressions)
        self.join_operators = tuple(join_operators)

    def get_format_keys(self) -> Set[str]:
        """
        Get required format keys.

        Returns:
            A set of keys.
        """
        result = set()
        for expr in self.expressions:
            result.update(expr.get_format_keys())
        return result

    def get_format_values(self) -> Set[str]:
        """
        Get required format values without value postfix.

        Returns:
            A set of keys.
        """
        result = set()
        for expr in self.expressions:
            result.update(expr.get_format_values())
        return result

    def get_operators(self) -> Set[ConditionExpressionOperatorStr]:
        """
        Get a set of all operators that used in expession group.

        Returns:
            A set of `ConditionExpressionOperator`.
        """
        result = set()
        for expression in self.expressions:
            result.update(expression.get_operators())
        return result

    def __or__(
        self, other: Union["ConditionExpression", "ConditionExpressionGroup"],
    ) -> "ConditionExpressionGroup":
        join_operators: List[ConditionExpressionJoinOperatorStr] = []
        if isinstance(other, ConditionExpressionGroup):
            join_operators.extend(self.join_operators)
            join_operators.append("OR")
            join_operators.extend(other.join_operators)
            expressions: List[ConditionExpression] = []
            expressions.extend(self.expressions)
            expressions.extend(other.expressions)
            return ConditionExpressionGroup(expressions=expressions, join_operators=join_operators)

        if isinstance(other, ConditionExpression):
            join_operators.extend(self.join_operators)
            join_operators.append("OR")
            expressions = []
            expressions.extend(self.expressions)
            expressions.append(other)
            return ConditionExpressionGroup(expressions=expressions, join_operators=join_operators)

        raise ExpressionError(f"Incompatible expression operation: {self.render()} AND {other}")

    def __and__(
        self, other: Union["ConditionExpression", "ConditionExpressionGroup"],
    ) -> "ConditionExpressionGroup":
        join_operators: List[ConditionExpressionJoinOperatorStr] = []
        if isinstance(other, ConditionExpressionGroup):
            join_operators.extend(self.join_operators)
            join_operators.append("AND")
            join_operators.extend(other.join_operators)
            expressions: List[ConditionExpression] = []
            expressions.extend(self.expressions)
            expressions.extend(other.expressions)
            return ConditionExpressionGroup(expressions=expressions, join_operators=join_operators)

        if isinstance(other, ConditionExpression):
            join_operators.extend(self.join_operators)
            join_operators.append("AND")
            expressions = []
            expressions.extend(self.expressions)
            expressions.append(other)
            return ConditionExpressionGroup(expressions=expressions, join_operators=join_operators)

        raise ExpressionError(f"Incompatible expression operation: {self.render()} AND {other}")

    def _render(self) -> str:
        """
        Render expression to string.

        Returns:
            A rendered expression as a string.
        """
        results: List[str] = []
        for index, expression in enumerate(self.expressions):
            if index:
                results.append(self.join_operators[index - 1])
            results.append(expression.render())

        return " ".join(results)


class UpdateExpression(BaseExpression):
    """
    Renderer for format-ready `UpdateExpression`.

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

    Arguments:
        args -- Keys to use SET expression, use to update values.
        update -- Keys to use SET expression, use to update values.
        set_if_not_exists -- Keys to use SET expression, use to add new keys.
        add -- Keys to use ADD expression, use to extend lists.
        delete -- Keys to use DELETE expression, use to subtract lists.
        remove -- Keys to use REMOVE expression, use to remove values.
    """

    def __init__(
        self,
        *args: str,
        update: Iterable[str] = tuple(),
        set_if_not_exists: Iterable[str] = tuple(),
        add: Iterable[str] = tuple(),
        delete: Iterable[str] = tuple(),
        remove: Iterable[str] = tuple(),
    ):
        self.update = tuple(args) + tuple(update)
        self.set_if_not_exists = tuple(set_if_not_exists)
        self.add = tuple(add)
        self.delete = tuple(delete)
        self.remove = tuple(remove)

    def validate_input_data(self, data: Dict[str, Any]) -> None:
        """
        Validate data that is used to format the expression.
        `ADD` and `DELETE` directives allow only sets and numbers.

        Arguments:
            data -- Data to validate.

        Raises:
            ExpressionError -- If data is invalid.
        """
        for key in self.add:
            if not isinstance(data[key], (set, int, float)):
                raise ExpressionError(f'Value "{key}" should be a set or a number, got {data[key]}')
        for key in self.delete:
            if not isinstance(data[key], (set, int, float)):
                raise ExpressionError(f'Value "{key}" should be a set or a number, got {data[key]}')

    def get_format_keys(self) -> Set[str]:
        """
        Get required format keys.

        Returns:
            A set of keys.
        """
        result: Set[str] = set()
        result.update(self.update, self.set_if_not_exists, self.add, self.delete, self.remove)
        return result

    def get_format_values(self) -> Set[str]:
        """
        Get required format values without value postfix.

        Returns:
            A set of keys.
        """
        result: Set[str] = set()
        result.update(self.update, self.set_if_not_exists, self.add, self.delete)
        return result

    def __and__(self: UpdateExpressionType, other: UpdateExpressionType) -> UpdateExpressionType:
        if isinstance(other, UpdateExpression):
            return self.__class__(
                update=self._extend_lists_dedup(self.update, other.update),
                set_if_not_exists=self._extend_lists_dedup(
                    self.set_if_not_exists, other.set_if_not_exists
                ),
                add=self._extend_lists_dedup(self.add, other.add),
                delete=self._extend_lists_dedup(self.delete, other.delete),
                remove=self._extend_lists_dedup(self.remove, other.remove),
            )

        raise ExpressionError(f"Incompatible expression operation: {self.render()} AND {other}")

    def _render(self) -> str:
        """
        Render expression to string.

        Returns:
            A rendered expression as a string.
        """
        add_list: List[str] = []
        set_list: List[str] = []
        delete_list: List[str] = []
        remove_list: List[str] = []
        for key in self.update:
            value_key = f"{key}{self._value_key_postfix}"
            set_list.append(f"{{{key}}} = {{{value_key}}}")
        for key in self.set_if_not_exists:
            value_key = f"{key}{self._value_key_postfix}"
            set_list.append(f"{{{key}}} = if_not_exists({{{key}}}, {{{value_key}}})")
        for key in self.add:
            value_key = f"{key}{self._value_key_postfix}"
            add_list.append(f"{{{key}}} {{{value_key}}}")
        for key in self.delete:
            value_key = f"{key}{self._value_key_postfix}"
            delete_list.append(f"{{{key}}} {{{value_key}}}")
        for key in self.remove:
            remove_list.append(f"{{{key}}}")

        result = []
        if set_list:
            result.append(f'SET {", ".join(set_list)}')
        if add_list:
            result.append(f'ADD {", ".join(add_list)}')
        if delete_list:
            result.append(f'DELETE {", ".join(delete_list)}')
        if remove_list:
            result.append(f'REMOVE {", ".join(remove_list)}')
        return " ".join(result)

    def get_operators(self) -> Set[ConditionExpressionOperatorStr]:
        """
        Get a set of all operators that used in expession group.
        """
        return set()


ConditionExpressionType = Union[ConditionExpression, ConditionExpressionGroup]
