from typing import Dict, Optional, List
from typing_extensions import Literal

from dynamo_query.dynamo_query_types import (
    GlobalSecondaryIndexTypeDef,
    LocalSecondaryIndexTypeDef,
    KeySchemaElementTypeDef,
    AttributeDefinitionTypeDef,
)


class DynamoTableIndex:
    """
    Constructor for DynamoDB global and local secondary index structures.

    Arguments:
        name -- Index name.
        sort_key -- Sort key attribute name.
        partition_key -- Partition key attribute name.

    Usage:

        ```python
        table_index = DynamoTableIndex("lsi_my_attr", "my_attr")
        table_index.as_dynamodb_dict()
        # {
        #     "IndexName": "lsi_my_attr",
        #     "KeySchema": [
        #         {"AttributeName": "pk", "KeyType": "HASH",},
        #         {"AttributeName": "my_attr", "KeyType": "RANGE"},
        #     ],
        #     "Projection": {"ProjectionType": "ALL"},
        # }
    """

    # Special name for primary table index
    PRIMARY = "primary"

    # Map to python types
    TYPES_MAP = {"S": str, "N": int, "B": bytes}

    def __init__(
        self,
        name: str,
        partition_key_name: str,
        sort_key_name: Optional[str],
        partition_key_type: Literal["S", "N", "B"] = "S",
        sort_key_type: Literal["S", "N", "B"] = "S",
    ):
        self._name = name
        self.partition_key_name = partition_key_name
        self.partition_key_type = partition_key_type
        self.sort_key_name = sort_key_name
        self.sort_key_type = sort_key_type

    @property
    def name(self) -> Optional[str]:
        """
        Get index name to use in queries.
        """
        if self._name == self.PRIMARY:
            return None

        return self._name

    def as_global_secondary_index(self) -> GlobalSecondaryIndexTypeDef:
        """
        Output a dictionary to use in `dynamo_client.create_table` method.

        Returns:
            A dict with index data.
        """
        key_schema: List[KeySchemaElementTypeDef]
        key_schema = [
            {"AttributeName": self.partition_key_name, "KeyType": "HASH"},
        ]
        if self.sort_key_name:
            key_schema.append({"AttributeName": self.sort_key_name, "KeyType": "RANGE"})

        return {
            "IndexName": self._name,
            "KeySchema": key_schema,
            "Projection": {"ProjectionType": "ALL"},
        }

    def as_local_secondary_index(self) -> LocalSecondaryIndexTypeDef:
        """
        Output a dictionary to use in `dynamo_client.create_table` method.

        Returns:
            A dict with index data.
        """
        key_schema: List[KeySchemaElementTypeDef]
        key_schema = [
            {"AttributeName": self.partition_key_name, "KeyType": "HASH"},
        ]
        if self.sort_key_name:
            key_schema.append({"AttributeName": self.sort_key_name, "KeyType": "RANGE"})

        return {
            "IndexName": self._name,
            "KeySchema": key_schema,
            "Projection": {"ProjectionType": "ALL"},
        }

    def as_key_schema(self) -> List[KeySchemaElementTypeDef]:
        """
        Output a dictionary to use in `dynamo_client.create_table` method.

        Returns:
            A dict with index data.
        """
        key_schema: List[KeySchemaElementTypeDef] = [
            {"AttributeName": self.partition_key_name, "KeyType": "HASH"},
        ]
        if self.sort_key_name:
            key_schema.append({"AttributeName": self.sort_key_name, "KeyType": "RANGE"})

        return key_schema

    def as_attribute_definitions(self) -> List[AttributeDefinitionTypeDef]:
        attribute_definitions: List[AttributeDefinitionTypeDef] = [
            {
                "AttributeName": self.partition_key_name,
                "AttributeType": self.partition_key_type,
            },
        ]
        if self.sort_key_name:
            attribute_definitions.append(
                {
                    "AttributeName": self.sort_key_name,
                    "AttributeType": self.sort_key_type,
                }
            )
        return attribute_definitions

    def __str__(self) -> str:
        return f"<DynamoTableIndex name={self.name}>"

    def get_query_data(
        self, partition_key: str, sort_key: Optional[str]
    ) -> Dict[str, str]:
        """
        Get query-ready data with `partition_key` and `sort_key` values.

        Arguments:
            partition_key -- Partition key value.
            sort_key -- Sort key value.

        Returns:
            Query-ready data.
        """
        if self.sort_key_name is None or sort_key is None:
            return {
                self.partition_key_name: partition_key,
            }

        return {
            self.partition_key_name: partition_key,
            self.sort_key_name: sort_key,
        }
