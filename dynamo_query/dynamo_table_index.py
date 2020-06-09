from typing import Dict, Iterable, List, Optional

from dynamo_query.dynamo_query_types import (
    AttributeDefinitionTypeDef,
    GlobalSecondaryIndexTypeDef,
    KeySchemaElementTypeDef,
    KeyTypeDef,
    LocalSecondaryIndexTypeDef,
    ProjectionTypeDef,
)


class DynamoTableIndex:
    """
    Constructor for DynamoDB global and local secondary index structures.

    Arguments:
        name -- Index name.
        partition_key_name -- Partition key attribute name.
        partition_key_type -- S(string)/N(number)/B(bytes).
        sort_key_name -- Sort key attribute name.
        sort_key_type -- S(string)/N(number)/B(bytes).
        read_capacity_units -- Read provisioned throughput units.
        write_capacity_units -- Write provisioned throughput units.
        projection -- Projection keys to include to index.

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
        partition_key_type: KeyTypeDef = "S",
        sort_key_type: KeyTypeDef = "S",
        read_capacity_units: Optional[int] = None,
        write_capacity_units: Optional[int] = None,
        projection: Iterable[str] = tuple(),
    ):
        self._name = name
        self.partition_key_name = partition_key_name
        self.partition_key_type = partition_key_type
        self.sort_key_name = sort_key_name
        self.sort_key_type = sort_key_type
        self.read_capacity_units = read_capacity_units
        self.write_capacity_units = write_capacity_units
        self.projection = projection

    @property
    def name(self) -> Optional[str]:
        """
        Get index name to use in queries.
        """
        if self._name == self.PRIMARY:
            return None

        return self._name

    def _get_projection(self) -> ProjectionTypeDef:
        if self.projection:
            return {
                "ProjectionType": "INCLUDE",
                "NonKeyAttributes": list(self.projection),
            }

        return {"ProjectionType": "ALL"}

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

        result: GlobalSecondaryIndexTypeDef = {
            "IndexName": self._name,
            "KeySchema": key_schema,
            "Projection": self._get_projection(),
        }
        if self.read_capacity_units and self.write_capacity_units:
            result["ProvisionedThroughput"] = {
                "ReadCapacityUnits": self.read_capacity_units,
                "WriteCapacityUnits": self.write_capacity_units,
            }
        return result

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

        result: LocalSecondaryIndexTypeDef = {
            "IndexName": self._name,
            "KeySchema": key_schema,
            "Projection": self._get_projection(),
        }
        return result

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
            {"AttributeName": self.partition_key_name, "AttributeType": self.partition_key_type,},
        ]
        if self.sort_key_name:
            attribute_definitions.append(
                {"AttributeName": self.sort_key_name, "AttributeType": self.sort_key_type,}
            )
        return attribute_definitions

    def __str__(self) -> str:
        return f"<DynamoTableIndex name={self.name}>"

    def get_query_data(self, partition_key: str, sort_key: Optional[str]) -> Dict[str, str]:
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
