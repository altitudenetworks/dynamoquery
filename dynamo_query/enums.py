"""
DynamoDB related enums.
"""
import enum
from typing import Set

__all__ = (
    "QueryType",
    "Operator",
)


class QueryType(enum.Enum):
    """
    Enum of DynamoQuery query types.

    Attributes:
        QUERY -- Used by DynamoQuery.build_query method
        SCAN -- Used by DynamoQuery.build_scan method
        GET_ITEM -- Used by DynamoQuery.build_get_item method
        UPDATE_ITEM -- Used by DynamoQuery.build_update_item method
        DELETE_ITEM -- Used by DynamoQuery.build_delete_item method
        BATCH_GET_ITEM -- Used by DynamoQuery.build_batch_get_item method
        BATCH_UPDATE_ITEM -- Used by DynamoQuery.build_batch_update_item method
        BATCH_DELETE_ITEM -- Used by DynamoQuery.build_batch_delete_item method
    """

    QUERY = "query"
    SCAN = "scan"
    GET_ITEM = "get_item"
    UPDATE_ITEM = "update_item"
    DELETE_ITEM = "delete_item"
    BATCH_GET_ITEM = "batch_get_item"
    BATCH_UPDATE_ITEM = "batch_update_item"
    BATCH_DELETE_ITEM = "batch_delete_item"


class Operator(enum.Enum):
    """
    Enum of operator types that can be used as postfixes in `ConditionExpression` keys.

    Attributes:
        EQ -- Rendered as `=` operator.
        NE -- Rendered as `<>` operator.
        IN -- Rendered as `IN` operator.
        GT -- Rendered as `>` operator.
        LT -- Rendered as `<` operator.
        GTE -- Rendered as `>=` operator.
        LTE -- Rendered as `<=` operator.
        BEGINS_WITH -- Rendered as `begins_with(<key>, <value>)` function.
        EXISTS -- Rendered as `attribute_exists(<key>)` function.
        NOT_EXISTS -- Rendered as `attribute_not_exists(<key>)` function.
        BETWEEN -- Rendered as `BETWEEN <value1> AND <value2>` operator.
        CONTAINS -- Rendered as `contains(<key>, <value>)` function.
    """

    EQ = "="
    NE = "<>"
    IN = "IN"
    GT = ">"
    LT = "<"
    GTE = ">="
    LTE = "<="
    BEGINS_WITH = "begins_with"
    EXISTS = "attribute_exists"
    NOT_EXISTS = "attribute_not_exists"
    BETWEEN = "BETWEEN"
    CONTAINS = "contains"

    @classmethod
    def values(cls) -> Set[str]:
        return set(cls)
