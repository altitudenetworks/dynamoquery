from typing import Dict, Text, Iterable, Callable, Any, TypeVar

from boto3.resources.factory import ServiceResource

from dynamo_query.data_table import DataTable

BaseExpression = TypeVar('BaseExpression')
ExpressionMap = Dict[Text, BaseExpression]
FormatDict = Dict[Text, Any]
TableKeys = Iterable[Text]
QueryMethod = Callable[[ServiceResource, DataTable, TableKeys], DataTable]
ExclusiveStartKey = Dict[Text, Any]
Boto3QueryMethod = Callable[..., Dict[Text, Any]]
TableResource = ServiceResource
