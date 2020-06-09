from typing import TYPE_CHECKING, Any, Dict, Iterable, Mapping, Set, TypeVar

if TYPE_CHECKING:
    from typing_extensions import Literal
    from mypy_boto3_application_autoscaling.client import ApplicationAutoScalingClient
    from mypy_boto3_application_autoscaling.type_defs import (
        TargetTrackingScalingPolicyConfigurationTypeDef,
    )
    from mypy_boto3_dynamodb.service_resource import Table
    from mypy_boto3_dynamodb.client import DynamoDBClient
    from mypy_boto3_dynamodb.type_defs import (
        GetItemOutputTypeDef,
        UpdateItemOutputTypeDef,
        DeleteItemOutputTypeDef,
        QueryOutputTypeDef,
        ScanOutputTypeDef,
        BatchGetItemOutputTypeDef,
        BatchWriteItemOutputTypeDef,
        CreateTableOutputTypeDef,
        LocalSecondaryIndexTypeDef,
        ProjectionTypeDef,
        GlobalSecondaryIndexTypeDef,
        KeySchemaElementTypeDef,
        AttributeDefinitionTypeDef,
    )

    BaseExpression = TypeVar("BaseExpression")
    ExpressionMap = Dict[str, BaseExpression]
    FormatDict = Dict[str, Any]
    TableKeys = Set[str]
    RecordType = Mapping[str, Any]
    RecordsType = Iterable[RecordType]
    ExclusiveStartKey = Dict[str, Any]
    ConditionExpressionOperatorStr = Literal[
        "=",
        "<>",
        "IN",
        ">",
        "<",
        ">=",
        "<=",
        "begins_with",
        "attribute_exists",
        "attribute_not_exists",
        "BETWEEN",
        "contains",
    ]
    ConditionExpressionJoinOperatorStr = Literal[
        "AND", "OR",
    ]

    ReturnValues = Literal["NONE", "ALL_OLD", "UPDATED_OLD", "ALL_NEW", "UPDATED_NEW"]
    ReturnItemCollectionMetrics = Literal["NONE", "SIZE"]
    ReturnConsumedCapacity = Literal["INDEXES", "TOTAL", "NONE"]
    KeyTypeDef = Literal["S", "N", "B"]
    SortKeyOperatorTypeDef = Literal["=", "begins_with"]
    ScalableDimensionTypeDef = Literal[
        "dynamodb:index:ReadCapacityUnits",
        "dynamodb:index:WriteCapacityUnits",
        "dynamodb:table:ReadCapacityUnits",
        "dynamodb:table:WriteCapacityUnits",
    ]
    MetricTypeTypeDef = Literal[
        "DynamoDBReadCapacityUtilization", "DynamoDBWriteCapacityUtilization"
    ]
    PartitionKeyOperatorTypeDef = Literal["="]
else:
    Literal = object
    Table = object
    DynamoDBClient = object
    BaseExpression = object
    GetItemOutputTypeDef = object
    UpdateItemOutputTypeDef = object
    DeleteItemOutputTypeDef = object
    QueryOutputTypeDef = object
    ScanOutputTypeDef = object
    BatchGetItemOutputTypeDef = object
    BatchWriteItemOutputTypeDef = object
    CreateTableOutputTypeDef = object
    LocalSecondaryIndexTypeDef = object
    GlobalSecondaryIndexTypeDef = object
    KeySchemaElementTypeDef = object
    AttributeDefinitionTypeDef = object
    ApplicationAutoScalingClient = object
    TargetTrackingScalingPolicyConfigurationTypeDef = object
    ExclusiveStartKey = object
    ExpressionMap = object
    FormatDict = object
    TableKeys = object
    ConditionExpressionJoinOperatorStr = object
    ConditionExpressionOperatorStr = object
    ReturnValues = object
    ReturnItemCollectionMetrics = object
    ReturnConsumedCapacity = object
    RecordType = object
    RecordsType = object
    KeyTypeDef = object
    SortKeyOperatorTypeDef = object
    ScalableDimensionTypeDef = object
    MetricTypeTypeDef = object
    PartitionKeyOperatorTypeDef = object
    ProjectionTypeDef = object
