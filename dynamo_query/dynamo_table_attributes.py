from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, List, Optional, Set

from dynamo_query.dynamo_query_types import AttributeDefinitionTypeDef
from dynamo_query.dynamo_table_index import DynamoTableIndex


class DynamoTableAttributes(ABC):
    # PK column name
    partition_key_name = "pk"

    # SK column name
    sort_key_name = "sk"

    # Set of table keys
    table_keys: Set[str] = {partition_key_name, sort_key_name}

    # GSI indexes list
    global_secondary_indexes: Iterable[DynamoTableIndex] = []

    # LSI indexes list
    local_secondary_indexes: Iterable[DynamoTableIndex] = []

    # Prefix to find items if you store several records in one table
    sort_key_prefix: Optional[str] = None

    # Primary global index
    primary_index = DynamoTableIndex(
        name=DynamoTableIndex.PRIMARY,
        partition_key_name=partition_key_name,
        sort_key_name=sort_key_name,
    )

    def __init__(self) -> None:
        self.attribute_definitions = self._get_attribute_definitions()
        self.attribute_types = self._get_attribute_types()

    @property
    @abstractmethod
    def table_name(self) -> str:
        pass

    def _get_attribute_definitions(self,) -> List[AttributeDefinitionTypeDef]:
        attribute_definitions: List[AttributeDefinitionTypeDef] = []
        attribute_names: Set[str] = set()
        indexes = (
            self.primary_index,
            *self.global_secondary_indexes,
            *self.local_secondary_indexes,
        )
        for index in indexes:
            index_attribute_definitions = index.as_attribute_definitions()
            for attribute_definition in index_attribute_definitions:
                attribute_name = attribute_definition["AttributeName"]
                if attribute_name in attribute_names:
                    continue
                attribute_definitions.append(attribute_definition)
                attribute_names.add(attribute_name)

        return attribute_definitions

    def _get_attribute_types(self) -> Dict[str, Any]:
        attribute_types: Dict[str, Any] = {}
        for attribute_definition in self.attribute_definitions:
            attribute_type = DynamoTableIndex.TYPES_MAP[attribute_definition["AttributeType"]]
            attribute_types[attribute_definition["AttributeName"]] = attribute_type
        return attribute_types
