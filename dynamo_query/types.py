from typing import Dict, Any, List

from typing_extensions import TypedDict


class ExecuteBoto3QueryReturnType(TypedDict, total=False):
    Item: Dict[str, Any]
    Attributes: Dict[str, Any]
    PreviousResponses: List[Any]
    LastEvaluatedKey: Dict[str, Any]
    Items: List[Dict[str, Any]]
    Responses: Dict[str, Any]
