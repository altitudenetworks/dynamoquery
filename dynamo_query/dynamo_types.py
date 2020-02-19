from typing import Dict, Iterable, Callable, Any, TypeVar, TYPE_CHECKING

from dynamo_query.data_table import DataTable

if TYPE_CHECKING:
    from mypy_boto3.dynamodb.service_resource import Table
    from mypy_boto3.dynamodb.client import DynamoDBClient
    from mypy_boto3.dynamodb.type_defs import (
        ClientGetItemResponseTypeDef,
        ClientUpdateItemResponseTypeDef,
        ClientDeleteItemResponseTypeDef,
        ClientQueryResponseTypeDef,
        ClientScanResponseTypeDef,
        ClientBatchGetItemResponseTypeDef,
        ClientBatchWriteItemResponseTypeDef,
    )

    BaseExpression = TypeVar("BaseExpression")
    ExpressionMap = Dict[str, BaseExpression]
    FormatDict = Dict[str, Any]
    TableKeys = Iterable[str]
    QueryMethod = Callable[[DataTable], DataTable]
    ExclusiveStartKey = Dict[str, Any]
    TableResource = Table

else:
    BaseExpression = object
    ExpressionMap = object
    FormatDict = object
    TableKeys = object
    QueryMethod = object
    ExclusiveStartKey = object
    TableResource = object
    ClientGetItemResponseTypeDef = object
    ClientUpdateItemResponseTypeDef = object
    ClientDeleteItemResponseTypeDef = object
    ClientQueryResponseTypeDef = object
    ClientScanResponseTypeDef = object
    ClientBatchGetItemResponseTypeDef = object
    ClientBatchWriteItemResponseTypeDef = object
    DynamoDBClient = object
