"""
Main import point for DynamoQuery.
"""
from dynamo_query.data_table import DataTable
from dynamo_query.dictclasses.dynamo_dictclass import DynamoDictClass
from dynamo_query.dictclasses.loose_dictclass import LooseDictClass
from dynamo_query.dynamo_query_main import DynamoQuery, DynamoQueryError
from dynamo_query.dynamo_table import DynamoTable
from dynamo_query.enums import Operator
from dynamo_query.expressions import ConditionExpression

DynamoRecord = DynamoDictClass

__all__ = (
    "DynamoQuery",
    "DynamoQueryError",
    "ConditionExpression",
    "Operator",
    "DataTable",
    "DynamoDictClass",
    "LooseDictClass",
    "DynamoRecord",
    "DynamoTable",
)
