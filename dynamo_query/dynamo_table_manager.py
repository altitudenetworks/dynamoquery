import logging
from abc import ABC, abstractmethod
from typing import Optional, cast

from dynamo_query.dynamo_query_types import CreateTableOutputTypeDef, DynamoDBClient, Table
from dynamo_query.dynamo_table_attributes import DynamoTableAttributes
from dynamo_query.lazy_logger import LazyLogger


class DynamoTableManager(ABC, LazyLogger):
    def __init__(
        self, table_attributes: DynamoTableAttributes, logger: Optional[logging.Logger] = None,
    ):
        self._table_attributes = table_attributes
        self._lazy_logger = logger

    @property
    @abstractmethod
    def table(self) -> Table:
        """
        Override this method to get DynamoDB Table resource.
        """

    @property
    def client(self) -> DynamoDBClient:
        return cast(DynamoDBClient, self.table.meta.client)

    def delete_table(self) -> None:
        """
        Delete the table from DynamoDB.

        Example:

            ```python
            # UserTableManager is a subclass of a DynamoTableManager
            user_table_manager = UserTableManager()

            # delete table
            user_table_manager.delete_table()
            ```
        """
        self.table.delete()

    def create_table(self) -> CreateTableOutputTypeDef:
        """
        Create a table in DynamoDB.

        Example:

            ```python
            # UserTableManager is a subclass of a DynamoTableManager
            user_table_manager = UserTableManager()

            # create a table with key schema and all indexes.
            user_table_manager.create_table()
            ```
        """
        global_secondary_indexes = [
            i.as_global_secondary_index() for i in self._table_attributes.global_secondary_indexes
        ]
        local_secondary_indexes = [
            i.as_local_secondary_index() for i in self._table_attributes.local_secondary_indexes
        ]

        return self.client.create_table(
            AttributeDefinitions=self._table_attributes.attribute_definitions,
            TableName=self.table.name,
            KeySchema=self._table_attributes.primary_index.as_key_schema(),
            GlobalSecondaryIndexes=global_secondary_indexes,
            LocalSecondaryIndexes=local_secondary_indexes,
        )

    def clear_table(self) -> None:
        """
        Clear full table in DynamoDB.

        Instead of deleting all rows from a big table, it is advised to delete and re-create
        the table as it is faster and cheaper

        Example:

            ```python
            # UserTableManager is a subclass of a DynamoTableManager
            user_table_manager = UserTableManager()

            # create a table with key schema and all indexes.
            user_table_manager.create_table()
            ```
        """
        self.delete_table()
        self.wait_until_not_exists()
        self.create_table()
        self.wait_until_exists()

    def wait_until_exists(self) -> None:
        """
        Proxy method for `resource.Table.wait_until_exists`.
        """
        self.table.wait_until_exists()

    def wait_until_not_exists(self) -> None:
        """
        Proxy method for `resource.Table.wait_until_not_exists`.
        """
        self.table.wait_until_not_exists()
