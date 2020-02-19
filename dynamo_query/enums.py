import enum


class DynamoQueryType(enum.Enum):
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


class ReturnConsumedCapacity(enum.Enum):
    """
    Enum of `ReturnConsumedCapacity` argument values for Boto3

    Attributes:
        INDEXES -- Add indexes only consumed capacity.
        TOTAL -- Add full consumed capacity.
        NONE -- Do not add consumed capacity.
    """

    INDEXES = "INDEXES"
    TOTAL = "TOTAL"
    NONE = "NONE"


class ReturnValues(enum.Enum):
    """
    Enum of `ReturnValues` argument values for Boto3

    Attributes:
        NONE -- Do not return object fields.
        ALL_OLD -- Return all field values before update operation.
        UPDATED_OLD -- Return updated field values before update operation.
        ALL_NEW -- Return all field values as they appear after update operation.
        UPDATED_NEW -- Return updated field values as they appear after update operation.
    """

    NONE = "NONE"
    ALL_OLD = "ALL_OLD"
    UPDATED_OLD = "UPDATED_OLD"
    ALL_NEW = "ALL_NEW"
    UPDATED_NEW = "UPDATED_NEW"


class ReturnItemCollectionMetrics(enum.Enum):
    """
    Enum of `ReturnItemCollectionMetrics` argument values for Boto3

    Attributes:
        NONE -- Do not Include statistics to response.
        SIZE -- Include size statistics to response.
    """

    NONE = "NONE"
    SIZE = "SIZE"


class ConditionExpressionOperator(enum.Enum):
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

    EQ = "eq"
    NE = "ne"
    IN = "in"
    GT = "gt"
    LT = "lt"
    GTE = "gte"
    LTE = "lte"
    BEGINS_WITH = "begins_with"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"
    BETWEEN = "between"
    CONTAINS = "contains"


class ConditionExpressionJoinOperator(enum.Enum):
    """
    Enum of operator types that join `ConditionExpression` in a group.

    Attributes:
        AND -- Rendered as `AND` operator.
        OR -- Rendered as `OR` operator.
    """

    AND = "AND"
    OR = "OR"
