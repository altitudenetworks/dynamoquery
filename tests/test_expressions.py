import pytest

from dynamo_query.expressions import (
    ExpressionError,
    Expression,
    ProjectionExpression,
    UpdateExpression,
    ConditionExpression,
)
from dynamo_query.enums import ConditionExpressionOperator


class TestExpression:
    result: Expression
    other: Expression

    def setup_method(self) -> None:
        self.result = Expression("{key} = {key1__value}")
        self.other = Expression("{key2} = {key2__value}")

    def test_init(self) -> None:
        assert self.result.data == "{key} = {key1__value}"
        assert self.other.data == "{key2} = {key2__value}"
        assert repr(self.result) == '<Expression "{key} = {key1__value}">'

    def test_methods(self) -> None:
        assert self.result.get_format_keys() == {"key"}
        assert self.result.get_format_values() == {"key1"}
        assert self.result.get_operators() == set()
        assert self.result.render() == "{key} = {key1__value}"

    def test_operators(self) -> None:
        and_result = self.result & self.other
        assert and_result.render() == "{key} = {key1__value} AND {key2} = {key2__value}"
        or_result = self.result | self.other
        assert or_result.render() == "{key} = {key1__value} OR {key2} = {key2__value}"


class TestProjectionExpression:
    result: ProjectionExpression
    other: ProjectionExpression

    def setup_method(self) -> None:
        self.result = ProjectionExpression("key1", "key2")
        self.other = ProjectionExpression("key2", "key3")

    def test_init(self) -> None:
        assert self.result.keys == ("key1", "key2")
        assert str(self.result) == "{key1}, {key2}"
        assert repr(self.result) == '<ProjectionExpression "{key1}, {key2}">'

    def test_methods(self) -> None:
        assert self.result.get_format_keys() == {"key1", "key2"}
        assert self.result.get_format_values() == set()
        assert self.result.get_operators() == set()
        assert self.result.render() == "{key1}, {key2}"

    def test_operators(self) -> None:
        and_result = self.result & self.other
        assert and_result.render() == "{key1}, {key2}, {key3}"


class TestConditionExpression:
    result: ConditionExpression
    other: ConditionExpression
    between: ConditionExpression

    def setup_method(self) -> None:
        self.result = ConditionExpression(
            "key", ConditionExpressionOperator.EQ, "value"
        )
        self.other = ConditionExpression("key2", "exists")
        self.between = ConditionExpression("key3", "between", ["value1", "value2"])

    def test_init(self) -> None:
        assert self.result.key == "key"
        assert self.result.operator == ConditionExpressionOperator.EQ
        assert self.result.value == "value"
        assert self.other.key == "key2"
        assert self.other.operator == ConditionExpressionOperator.EXISTS
        assert self.other.value is True
        assert ConditionExpression("key2", "eq").value == "key2"

        with pytest.raises(ExpressionError):
            ConditionExpression("key2", "between", ["value"])

    def test_methods(self) -> None:
        assert self.result.get_format_keys() == {"key"}
        assert self.other.get_format_keys() == {"key2"}
        assert self.result.get_format_values() == {"value"}
        assert self.other.get_format_values() == set()
        assert self.between.get_format_values() == {"value1", "value2"}
        assert self.result.get_operators() == {ConditionExpressionOperator.EQ}
        assert self.other.get_operators() == {ConditionExpressionOperator.EXISTS}
        assert self.result.render() == "{key} = {value__value}"
        assert self.other.render() == "attribute_exists({key2})"
        assert (
            self.between.render()
            == "{key3} BETWEEN {value1__value} AND {value2__value}"
        )

    def test_operators(self) -> None:
        and_result = self.result & self.other
        assert (
            and_result.render() == "{key} = {value__value} AND attribute_exists({key2})"
        )
        or_result = self.result | self.other
        assert (
            or_result.render() == "{key} = {value__value} OR attribute_exists({key2})"
        )

        group_and_result = self.between & or_result
        assert group_and_result.render() == (
            "{key3} BETWEEN {value1__value} AND {value2__value}"
            " AND {key} = {value__value} OR attribute_exists({key2})"
        )
        group_or_result = self.between | and_result
        assert group_or_result.render() == (
            "{key3} BETWEEN {value1__value} AND {value2__value}"
            " OR {key} = {value__value} AND attribute_exists({key2})"
        )


class TestUpdateExpression:
    result: UpdateExpression
    other: UpdateExpression

    def setup_method(self) -> None:
        self.result = UpdateExpression("key1", "key2")
        self.other = UpdateExpression("key3", remove=["key4"])

    def test_init(self) -> None:
        assert self.result.update == ("key1", "key2")
        assert self.result.remove == tuple()
        assert self.other.update == ("key3",)
        assert self.other.remove == ("key4",)

    def test_methods(self) -> None:
        assert self.result.get_format_keys() == {"key1", "key2"}
        assert self.result.get_format_values() == {"key1", "key2"}
        assert self.result.get_operators() == set()
        assert self.other.get_format_keys() == {"key3", "key4"}
        assert self.other.get_format_values() == {"key3"}
        assert self.other.get_operators() == set()

    def test_validate_input_data(self) -> None:
        self.result.validate_input_data({})
        check = UpdateExpression(add=["add"], delete=["delete"])
        check.validate_input_data({"add": 1, "delete": 2.4})

        with pytest.raises(ExpressionError):
            check.validate_input_data({"add": 1, "delete": "my_key"})

        with pytest.raises(ExpressionError):
            check.validate_input_data({"add": "my_key", "delete": 4.5})

    def test_render(self) -> None:
        assert (
            self.result.render() == "SET {key1} = {key1__value}, {key2} = {key2__value}"
        )
        assert self.other.render() == "SET {key3} = {key3__value} REMOVE {key4}"
        assert UpdateExpression(
            add=["add", "add2"],
            update=["update", "update2"],
            delete=["delete", "delete2"],
            remove=["remove", "remove2"],
        ).render() == (
            "SET {update} = {update__value}, {update2} = {update2__value}"
            " ADD {add} {add__value}, {add2} {add2__value}"
            " DELETE {delete} {delete__value}, {delete2} {delete2__value}"
            " REMOVE {remove}, {remove2}"
        )

    def test_operators(self) -> None:
        and_result = self.result & self.other
        assert and_result.render() == (
            "SET {key1} = {key1__value}, {key2} = {key2__value},"
            " {key3} = {key3__value} REMOVE {key4}"
        )
