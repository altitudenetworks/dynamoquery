import datetime
import logging
from abc import abstractmethod, abstractproperty
from typing import (
    Any,
    Dict,
    Generic,
    Iterable,
    Iterator,
    Mapping,
    Optional,
    Set,
    List,
    TypeVar,
    Union,
    cast,
)

from typing_extensions import Literal

from dynamo_query.data_table import DataTable
from dynamo_query.dynamo_query_main import DynamoQuery
from dynamo_query.dynamo_table_index import DynamoTableIndex
from dynamo_query.expressions import ConditionExpression, ConditionExpressionGroup
from dynamo_query.dynamo_query_types import (
    DynamoDBClient,
    Table,
    AttributeDefinitionTypeDef,
    CreateTableOutputTypeDef,
)
from dynamo_query.lazy_logger import LazyLogger
from dynamo_query import json_tools

__all__ = ("DynamoTable", "DynamoTableError")

DynamoRecord = TypeVar("DynamoRecord", bound=Mapping[str, Any])


class DynamoTableError(BaseException):
    """
    Main error for `DynamoTable` class.

    Arguments:
        message -- Error message.
        data -- Addition JSON-serializeable data.
    """

    def __init__(self, message: str, data: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.data = data

    def __str__(self) -> str:
        if self.data is not None:
            return f"{self.message} data={json_tools.dumps(self.data)}"
        return self.message


class DynamoTable(Generic[DynamoRecord], LazyLogger):
    """
    DynamoDB table manager, uses `DynamoQuery` underneath.

    Arguments:
        logger -- `logging.Logger` instance.

    Example:
        ```python
        from typing_extensions import TypedDict
        from dynamo_query import DynamoTable

        # first, define your record
        class UserRecord(TypedDict, total=False):
            pk: str
            email: str
            name: str
            points: int


        # Create your dynamo table manager with your record class
        class UserTable(DynamoTable[UserRecord]):
            # provide a set of your table keys
            table_keys = {'pk'}

            # use this property to define your table name
            @property
            def table(self) -> str:
                return "my_table"

            # define how to get PK from a record
            def get_partition_key(self, record: UserRecord) -> str:
                return record["email"]

            # we do not have a sort key in our table
            def get_sort_key(self, record: UserRecord) -> None:
                return None

            # specify some GSIs
            global_secondary_indexes = [
                DynamoTableIndex("gsi_name", "name", None),
                DynamoTableIndex("gsi_email_age", "email", "age"),
            ]

        # and now we can create our table in DynamoDB
        user_table = UserTable()
        user_table.create_table()
        ```
    """

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

    def __init__(
        self, logger: Optional[logging.Logger] = None,
    ):
        self._lazy_logger = logger
        self._attribute_definitions = self._get_attribute_definitions()
        self._attribute_types = self._get_attribute_types()

    @abstractproperty
    def table(self) -> Table:
        """
        Override this method to get DynamoDB Table resource.
        """

    @property
    def client(self) -> DynamoDBClient:
        return cast(DynamoDBClient, self.table.meta.client)

    @abstractmethod
    def get_partition_key(self, record: DynamoRecord) -> Any:
        """
        Override this method to get PK from a record.
        """

    @abstractmethod
    def get_sort_key(self, record: DynamoRecord) -> Any:
        """
        Override this method to get SK from a record.
        """

    def _get_partition_key(self, record: DynamoRecord) -> Any:
        if self.partition_key_name in record:
            return record[self.partition_key_name]

        return self.get_partition_key(record)

    def _get_sort_key(self, record: DynamoRecord) -> Any:
        if self.sort_key_name in record:
            return record[self.sort_key_name]

        return self.get_sort_key(record)

    def delete_table(self) -> None:
        """
        Delete the table from DynamoDB.

        Example:

            ```python
            # UserTable is a subclass of a DynamoTable
            user_table = UserTable()

            # delete table
            UserTable.delete_table()
            ```
        """
        self.table.delete()

    def create_table(self) -> CreateTableOutputTypeDef:
        """
        Create a table in DynamoDB.

        Example:

            ```python
            # UserTable is a subclass of a DynamoTable
            user_table = UserTable()

            # create a table with key schema and all indexes.
            UserTable.create_table()
            ```
        """
        global_secondary_indexes = [
            i.as_global_secondary_index() for i in self.global_secondary_indexes
        ]
        local_secondary_indexes = [
            i.as_local_secondary_index() for i in self.local_secondary_indexes
        ]

        return self.client.create_table(
            AttributeDefinitions=self._attribute_definitions,
            TableName=self.table.name,
            KeySchema=self.primary_index.as_key_schema(),
            GlobalSecondaryIndexes=global_secondary_indexes,
            LocalSecondaryIndexes=local_secondary_indexes,
        )

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
        for attribute_definition in self._attribute_definitions:
            attribute_type = DynamoTableIndex.TYPES_MAP[
                attribute_definition["AttributeType"]
            ]
            attribute_types[attribute_definition["AttributeName"]] = attribute_type
        return attribute_types

    # pylint: disable=no-self-use
    def normalize_record(self, record: DynamoRecord) -> DynamoRecord:
        """
        Modify record before upsert.

        Arguments:
            record -- Record for upsert.

        Returns:
            Normalized record.
        """
        return record

    def validate_record_attributes(self, record: DynamoRecord) -> None:
        """
        Check that all index keys are set correctly in record.

        Arguments:
            record -- Record for upsert.

        Raises:
            DynamoTableError -- If index key is missing.
        """
        for attribute_name, attribute_type in self._attribute_types.items():
            if attribute_name not in record:
                raise DynamoTableError(
                    f"Attribute {attribute_name} is not set in record.", data=record,
                )
            value = record[attribute_name]
            if not isinstance(value, attribute_type):
                raise DynamoTableError(
                    f"Attribute {attribute_name} has invalid type, {attribute_type} expected.",
                    data=record,
                )

    def _yield_from_query(
        self, query: DynamoQuery, data: Dict[str, Any], limit: Optional[int] = None
    ) -> Iterator[DynamoRecord]:
        records_count = 0
        while True:
            results_data_table = query.table(
                table_keys=self.table_keys, table=self.table,
            ).execute_dict(data)

            for record in results_data_table.get_records():
                if limit is not None and records_count >= limit:
                    return

                records_count += 1
                yield record

            if not query.has_more_results():
                return

    def clear_table(
        self,
        partition_key: Optional[str] = None,
        partition_key_prefix: Optional[str] = None,
        sort_key: Optional[str] = None,
        sort_key_prefix: Optional[str] = None,
        index: DynamoTableIndex = primary_index,
        filter_expression: Optional[ConditionExpression] = None,
        limit: Optional[int] = None,
    ) -> None:
        """
        Remove records from DB.

        If `partition_key` and `partition_key_prefix` are None - deletes all records.

        Arguments:
            partition_key -- Partition key value.
            sort_key -- Sort key value.
            partition_key_prefix -- Partition key prefix value.
            sort_key_prefix -- Sort key prefix value.
            index -- DynamoTableIndex instance, primary index is used if not provided.
            filter_expression -- Query filter expression.
            limit -- Max number of results.
        """
        if partition_key is not None:
            records = self.query(
                partition_key=partition_key,
                index=index,
                sort_key=sort_key,
                sort_key_prefix=sort_key_prefix,
                filter_expression=filter_expression,
                limit=limit,
                projection=self.table_keys,
            )
        elif partition_key is None and partition_key_prefix is not None:
            records = self.scan(
                filter_expression=ConditionExpression(
                    self.partition_key_name, operator="begins_with"
                ),
                data={self.partition_key_name: partition_key_prefix},
                projection=self.table_keys,
            )
        else:
            records = self.scan(projection=self.table_keys)

        existing_records = DataTable[DynamoRecord]().add_record(*records)

        if not existing_records:
            return

        DynamoQuery.build_batch_delete_item(logger=self._logger).table(
            table_keys=self.table_keys, table=self.table,
        ).execute(existing_records)

    def batch_get(self, data_table: DataTable[DynamoRecord]) -> DataTable[DynamoRecord]:
        """
        Get multuple records as a DataTable from DB.

        `data_table` must have all columns to calculate table keys.

        Example:

            ```python
            # UserTable is a subclass of a DynamoTable
            user_table = UserTable()

            # we should provide table keys or fields to calculate them
            # in our case, PK is calculated from `email` field.
            users_table = DataTable[UserRecord]().add_record(
                {
                    "email": "puppy@gmail.com",
                },
                {
                    "email": "elon@gmail.com",
                },
            )
            user_records = user_table.batch_get(users_table)

            for user_record in user_records:
                # print found records
                # if record was not found - it will still be returned
                # but only with the data you provided
                print(user_record)
            ```

        Arguments:
            data_table -- Request data table.

        Returns:
            DataTable with existing records.
        """
        if not data_table:
            return DataTable()
        get_data_table = DataTable[DynamoRecord]()
        for record in data_table.get_records():
            partition_key = self._get_partition_key(record)
            sort_key = self._get_sort_key(record)
            new_record = cast(
                DynamoRecord,
                {
                    self.partition_key_name: partition_key,
                    self.sort_key_name: sort_key,
                    **record,
                },
            )
            get_data_table.add_record(new_record)

        results: DataTable[DynamoRecord] = DynamoQuery.build_batch_get_item(
            logger=self._logger,
        ).table(table_keys=self.table_keys, table=self.table,).execute(
            data_table=get_data_table,
        )
        return results

    def batch_delete(
        self, data_table: DataTable[DynamoRecord]
    ) -> DataTable[DynamoRecord]:
        """
        Delete multuple records as a DataTable from DB.

        `data_table` must have all columns to calculate table keys.

        Example:

            ```python
            # UserTable is a subclass of a DynamoTable
            user_table = UserTable()

            # we should provide table keys or fields to calculate them
            # in our case, PK is calculated from `email` field.
            users_table = DataTable[UserRecord]().add_record(
                {
                    "email": "puppy@gmail.com",
                },
                {
                    "email": "elon@gmail.com",
                },
            )
            deleted_records = user_table.batch_delete(users_table)

            for deleted_record in deleted_records:
                # print deleted_record records
                # if record was not found - it will still be returned
                # but only with the data you provided
                print(deleted_record)
            ```

        Arguments:
            data_table -- Request data table.

        Returns:
            DataTable with deleted records.
        """
        if not data_table:
            return DataTable()

        delete_data_table = DataTable[DynamoRecord]()
        for record in data_table.get_records():
            partition_key = self._get_partition_key(record)
            sort_key = self._get_sort_key(record)
            new_record = cast(
                DynamoRecord,
                {self.partition_key_name: partition_key, self.sort_key_name: sort_key},
            )
            delete_data_table.add_record(new_record)

        results: DataTable[DynamoRecord] = DynamoQuery.build_batch_delete_item(
            logger=self._logger,
        ).table(table_keys=self.table_keys, table=self.table,).execute(
            delete_data_table
        )
        return results

    def batch_upsert(
        self,
        data_table: DataTable[DynamoRecord],
        set_if_not_exists_keys: Iterable[str] = (),
    ) -> DataTable[DynamoRecord]:
        """
        Upsert multuple records as a DataTable to DB.

        `data_table` must have all columns to calculate table keys.

        Sets `dt_created` field equal to current UTC datetime if a record was created.
        Sets `dt_modified` field equal to current UTC datetime.

        Example:

            ```python
            # UserTable is a subclass of a DynamoTable
            user_table = UserTable()

            # we should provide table keys or fields to calculate them
            # in our case, PK is calculated from `email` field.
            users_table = DataTable[UserRecord]().add_record(
                {
                    "email": "puppy@gmail.com",
                    "name": "Doge Barky",
                    "age": 20,
                },
                {
                    "email": "elon@gmail.com",
                    "name": "Elon Musk",
                    "age": 5289,
                },
            )
            upserted_records = user_table.batch_upsert(users_table)

            for upserted_record in upserted_records:
                # print created and updated records
                print(upserted_record)
            ```

        Arguments:
            data_table -- Request DataTable.
            set_if_not_exists_keys -- List of keys to set only if they no do exist in DB.

        Returns:
            A DataTable with upserted results.
        """
        if not data_table:
            return DataTable[DynamoRecord]()

        set_if_not_exists = set(set_if_not_exists_keys)
        existing_records = self.batch_get(data_table)
        now = datetime.datetime.utcnow()
        now_str = now.isoformat()

        update_data_table: DataTable[DynamoRecord] = DataTable()
        for record_index, record in enumerate(existing_records.get_records()):
            updated_record = data_table.get_record(record_index)
            preserve_keys_record: Dict[str, Any] = {}
            for key in set_if_not_exists:
                if key in record:
                    preserve_keys_record[key] = record[key]

            new_record = cast(
                DynamoRecord,
                {
                    **record,
                    **updated_record,
                    **preserve_keys_record,
                    "dt_created": record.get("dt_created") or now_str,
                    "dt_modified": now_str,
                },
            )
            normalized_record = self.normalize_record(new_record)
            self.validate_record_attributes(normalized_record)
            update_data_table.add_record(normalized_record)

        results: DataTable[DynamoRecord] = DynamoQuery.build_batch_update_item(
            logger=self._logger,
        ).table(table_keys=self.table_keys, table=self.table,).execute(
            update_data_table
        )
        return results

    def get_record(self, record: DynamoRecord) -> Optional[DynamoRecord]:
        """
        Get Record from DB.

        `record` must have all fields to calculate table keys.

        Example:

            ```python
            # UserTable is a subclass of a DynamoTable
            user_table = UserTable()

            # we should provide table keys or fields to calculate them
            # in our case, PK is calculated from `email` field.
            user_record = user_table.get_record({
                "email": "suspicious@gmail.com",
            })

            if user_record is None:
                # no record found
                pass
            else:
                # print found record
                print(user_record)
            ```

        Arguments:
            record -- Record with required fields for sort and partition keys.

        Returns:
            A dict with record data or None.
        """
        partition_key = self._get_partition_key(record)
        sort_key = self._get_sort_key(record)
        result = (
            DynamoQuery.build_get_item(logger=self._logger)
            .table(table_keys=self.table_keys, table=self.table,)
            .execute_dict(
                {self.partition_key_name: partition_key, self.sort_key_name: sort_key}
            )
        )
        if set(result.get_set_column_names()).issubset(self.table_keys):
            return None

        return cast(DynamoRecord, result.get_record(0))

    def upsert_record(
        self,
        record: DynamoRecord,
        condition_expression: Optional[ConditionExpression] = None,
        set_if_not_exists_keys: Iterable[str] = (),
        extra_data: Dict[str, Any] = None,
    ) -> DynamoRecord:
        """
        Upsert Record to DB.

        `record` must have all fields to calculate table keys.

        Sets `dt_created` field equal to current UTC datetime if a record was created.
        Sets `dt_modified` field equal to current UTC datetime.

        Example:

            ```python
            # UserTable is a subclass of a DynamoTable
            user_table = UserTable()

            # we should provide table keys or fields to calculate them
            # in our case, PK is calculated from `email` field.
            user_record = user_table.upsert_record(
                {
                    "email": "newuser@gmail.com",
                    "name": "Somebody Oncetoldme"
                    "age": 23,
                },
                set_if_not_exists_keys=["age"], # set age if it does not exist in DB yet.
            )

            # print upserted record
            print(user_record)
            ```

        Arguments:
            record -- Record to insert/update.
            condition_expression -- Condition for update.
            set_if_not_exists_keys -- List of keys to set only if they no do exist in DB.
            extra_data -- Data for query.

        Returns:
            A dict with updated record data.
        """
        set_if_not_exists = set(set_if_not_exists_keys)
        set_if_not_exists.add("dt_created")

        partition_key = self._get_partition_key(record)
        sort_key = self._get_sort_key(record)

        now = datetime.datetime.utcnow()
        now_str = now.isoformat()

        new_record = cast(
            DynamoRecord,
            {
                self.partition_key_name: partition_key,
                self.sort_key_name: sort_key,
                **record,
                **(extra_data or {}),
                "dt_modified": now_str,
                "dt_created": now_str,
            },
        )
        new_record = self.normalize_record(new_record)
        update_keys = set(new_record.keys()) - self.table_keys - set_if_not_exists
        update_keys.add("dt_modified")
        result: DataTable[DynamoRecord] = (
            DynamoQuery.build_update_item(
                condition_expression=condition_expression, logger=self._logger,
            )
            .update(update=update_keys, set_if_not_exists=set_if_not_exists)
            .table(table_keys=self.table_keys, table=self.table,)
            .execute_dict(cast(Dict[str, Any], new_record))
        )
        return result.get_record(0)

    def delete_record(
        self,
        record: DynamoRecord,
        condition_expression: Optional[ConditionExpression] = None,
    ) -> Optional[DynamoRecord]:
        """
        Delete Record from DB.

        `record` must have all fields to calculate table keys.

        Example:

            ```python
            # UserTable is a subclass of a DynamoTable
            user_table = UserTable()

            # we should provide table keys or fields to calculate them
            # in our case, PK is calculated from `email` field.
            deleted_record = user_table.delete_record({
                "email": "cheater@gmail.com",
            })

            if deleted_record is None:
                # no record found, so nothing was deleted
            else:
                # print deleted record
                print(user_record)
            ```

        Arguments:
            record -- Record with required fields for sort and partition keys.
            condition_expression -- Condition for delete.

        Returns:
            A dict with record data or None.
        """
        partition_key = self._get_partition_key(record)
        sort_key = self._get_sort_key(record)
        result: DataTable[DynamoRecord] = DynamoQuery.build_delete_item(
            condition_expression=condition_expression, logger=self._logger,
        ).table(table=self.table, table_keys=self.table_keys).execute_dict(
            {self.partition_key_name: partition_key, self.sort_key_name: sort_key},
        )
        if not result:
            return None
        return result.get_record(0)

    def scan(
        self,
        filter_expression: Optional[ConditionExpression] = None,
        projection: Iterable[str] = tuple(),
        data: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> Iterator[DynamoRecord]:
        """
        List table records.

        Example:

            ```python
            # UserTable is a subclass of a DynamoTable
            user_table = UserTable()

            user_records = user_table.scan(
                # get only users older than ...
                # we will provide values in data
                filter_expression=ConditionExpression("age", "<="),

                # get only first 5 results
                limit=5,

                # get only name and email fields
                projection=("name", "email"),

                # ...older than 45 years
                data= {"age": 45}
            )

            for user_record in user_records:
                print(user_record)
            ```

        Arguments:
            filter_expression -- Query filter expression.
            scan_index_forward -- Whether to scan index from the beginning.
            projection -- Record fields to return, by default returns all fields.
            limit -- Max number of results.
        """
        query = DynamoQuery.build_scan(
            filter_expression=filter_expression, logger=self._logger,
        )
        if limit:
            query.limit(limit)

        if projection:
            query.projection(*projection)

        query_data = {"key": "value"}
        if data:
            query_data.update(data)

        for record in self._yield_from_query(query, data=query_data, limit=limit):
            yield record

    def query(
        self,
        partition_key: str,
        index: DynamoTableIndex = primary_index,
        sort_key: Optional[str] = None,
        sort_key_prefix: Optional[str] = None,
        filter_expression: Optional[ConditionExpression] = None,
        scan_index_forward: bool = True,
        projection: Iterable[str] = tuple(),
        data: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> Iterator[DynamoRecord]:
        """
        Query table records by index.

        Example:

            ```python
            # UserTable is a subclass of a DynamoTable
            user_table = UserTable()

            user_records = user_table.query(
                # query by our PK
                partition_key="new_users",

                # and SK starting with `email_`
                sort_key_prefix="email_",

                # get only users older than ...
                # we will provide values in data
                filter_expression=ConditionExpression("age", "<="),

                # get only first 5 results
                limit=5,

                # get only name and email fields
                projection=("name", "email"),

                # ...older than 45 years
                data= {"age": 45}

                # start with the newest records
                scan_index_forward=False,
            )

            for user_record in user_records:
                print(user_record)
            ```

        Arguments:
            partition_key -- Partition key value.
            index -- DynamoTableIndex instance, primary index is used if not provided.
            sort_key -- Sort key value.
            sort_key_prefix -- Sort key prefix value.
            filter_expression -- Query filter expression.
            scan_index_forward -- Whether to scan index from the beginning.
            projection -- Record fields to return, by default returns all fields.
            limit -- Max number of results.

        Yields:
            Matching record.
        """
        sort_key_operator: Literal["=", "begins_with"] = "="
        partition_key_operator: Literal["="] = "="
        if sort_key_prefix is not None:
            sort_key_operator = "begins_with"
            sort_key = sort_key_prefix

        if partition_key is None:
            raise DynamoTableError("partition_key should be set.")

        key_condition_expression: Union[
            ConditionExpression, ConditionExpressionGroup
        ] = ConditionExpression(
            index.partition_key_name, operator=partition_key_operator
        )
        if sort_key is not None and index.sort_key_name is not None:
            key_condition_expression = key_condition_expression & ConditionExpression(
                index.sort_key_name, operator=sort_key_operator,
            )
        query = DynamoQuery.build_query(
            index_name=index.name,
            key_condition_expression=key_condition_expression,
            filter_expression=filter_expression,
            scan_index_forward=scan_index_forward,
            logger=self._logger,
        )
        if limit:
            query.limit(limit)

        if projection:
            query.projection(*projection)

        query_data = index.get_query_data(partition_key, sort_key)
        if data:
            query_data.update(data)

        for record in self._yield_from_query(query, data=query_data, limit=limit):
            yield record

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
