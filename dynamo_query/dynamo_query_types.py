from typing import TYPE_CHECKING, Any, Dict, Iterable, Mapping, Set

if TYPE_CHECKING:
    from mypy_boto3_application_autoscaling.client import ApplicationAutoScalingClient
    from mypy_boto3_application_autoscaling.type_defs import (
        TargetTrackingScalingPolicyConfigurationTypeDef,
    )
    from mypy_boto3_dynamodb.client import DynamoDBClient
    from mypy_boto3_dynamodb.literals import (
        ConditionalOperatorType,
        ReturnConsumedCapacityType,
        ReturnItemCollectionMetricsType,
        ReturnValueType,
        ScalarAttributeTypeType,
    )
    from mypy_boto3_dynamodb.service_resource import Table
    from mypy_boto3_dynamodb.type_defs import (
        AttributeDefinitionTypeDef,
        BatchGetItemOutputTypeDef,
        BatchWriteItemOutputTypeDef,
        CreateTableOutputTypeDef,
        DeleteItemOutputTypeDef,
        GetItemOutputTypeDef,
        GlobalSecondaryIndexTypeDef,
        KeySchemaElementTypeDef,
        LocalSecondaryIndexTypeDef,
        ProjectionTypeDef,
        ProvisionedThroughputTypeDef,
        QueryOutputTypeDef,
        ScanOutputTypeDef,
        UpdateItemOutputTypeDef,
    )
    from typing_extensions import Literal

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
    FormatDict = object
    TableKeys = object
    ConditionalOperatorType = object
    ConditionExpressionOperatorStr = object
    ReturnValueType = object
    ReturnItemCollectionMetricsType = object
    ReturnConsumedCapacityType = object
    RecordType = object
    RecordsType = object
    ScalarAttributeTypeType = object
    SortKeyOperatorTypeDef = object
    ScalableDimensionTypeDef = object
    MetricTypeTypeDef = object
    PartitionKeyOperatorTypeDef = object
    ProjectionTypeDef = object
    ProvisionedThroughputTypeDef = object

__all__ = (
    "Literal",
    "Table",
    "DynamoDBClient",
    "GetItemOutputTypeDef",
    "UpdateItemOutputTypeDef",
    "DeleteItemOutputTypeDef",
    "QueryOutputTypeDef",
    "ScanOutputTypeDef",
    "BatchGetItemOutputTypeDef",
    "BatchWriteItemOutputTypeDef",
    "CreateTableOutputTypeDef",
    "LocalSecondaryIndexTypeDef",
    "GlobalSecondaryIndexTypeDef",
    "KeySchemaElementTypeDef",
    "AttributeDefinitionTypeDef",
    "ApplicationAutoScalingClient",
    "TargetTrackingScalingPolicyConfigurationTypeDef",
    "ExclusiveStartKey",
    "FormatDict",
    "TableKeys",
    "ConditionalOperatorType",
    "ProvisionedThroughputTypeDef",
    "ConditionExpressionOperatorStr",
    "ReturnValueType",
    "ReturnItemCollectionMetricsType",
    "ReturnConsumedCapacityType",
    "RecordType",
    "RecordsType",
    "ScalarAttributeTypeType",
    "SortKeyOperatorTypeDef",
    "ScalableDimensionTypeDef",
    "MetricTypeTypeDef",
    "PartitionKeyOperatorTypeDef",
    "ProjectionTypeDef",
)
