import datetime
import logging
from abc import ABC, abstractmethod
from typing import (
    Any,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Type,
    TypeVar,
    Union,
    cast,
)

from dynamo_query import json_tools
from dynamo_query.data_table import DataTable
from dynamo_query.dictclasses.dynamo_dictclass import DynamoDictClass
from dynamo_query.dictclasses.loose_dictclass import LooseDictClass
from dynamo_query.dynamo_query_main import DynamoQuery
from dynamo_query.dynamo_query_types import (
    AttributeDefinitionTypeDef,
    CreateTableOutputTypeDef,
    DynamoDBClient,
    PartitionKeyOperatorTypeDef,
    SortKeyOperatorTypeDef,
    Table,
)
from dynamo_query.dynamo_table_index import DynamoTableIndex
from dynamo_query.expressions import ConditionExpression, ConditionExpressionType
from dynamo_query.lazy_logger import LazyLogger
from dynamo_query.utils import chunkify

__all__ = ("DynamoTable", "DynamoTableError")

_RecordType = TypeVar("_RecordType", bound=DynamoDictClass)


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


class DynamoTable(Generic[_RecordType], LazyLogger, ABC):
    """
    DynamoDB table manager, uses `DynamoQuery` underneath.

    Arguments:
        logger -- `logging.Logger` instance.

    Example:
        ```python
        from dynamo_query import DynamoTable, DynamoRecord
        from typing import Optional

        class UserRecord(DynamoRecord):
            pk: str
            email: str
            name: str
            points: Optional[int] = None

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
                return record.email

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
    partition_key_name: str = "pk"

    # SK column name
    sort_key_name: str = "sk"

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

    # class to use as DynamoQuery for easier subclassing
    dynamo_query_class: Type[DynamoQuery] = DynamoQuery

    # ProvisionedThroughput parameters
    read_capacity_units: Optional[int] = None
    write_capacity_units: Optional[int] = None

    record_class: Type[_RecordType] = LooseDictClass  # type: ignore

    def __init__(self, logger: Optional[logging.Logger] = None,) -> None:
        self._lazy_logger = logger
        self._attribute_definitions = self._get_attribute_definitions()
        self._attribute_types = self._get_attribute_types()

        for global_secondary_index in self.global_secondary_indexes:
            if not global_secondary_index.read_capacity_units and self.read_capacity_units:
                global_secondary_index.read_capacity_units = self.read_capacity_units
            if not global_secondary_index.write_capacity_units and self.write_capacity_units:
                global_secondary_index.write_capacity_units = self.write_capacity_units

    @property
    @abstractmethod
    def table(self) -> Table:
        """
        Override this method to get DynamoDB Table resource.
        """

    @property
    def client(self) -> DynamoDBClient:
        return cast(DynamoDBClient, self.table.meta.client)

    @property
    def max_batch_size(self) -> int:
        return self.dynamo_query_class.MAX_BATCH_SIZE

    def get_partition_key(self, record: _RecordType) -> Any:
        """
        Override this method to get PK from a record.
        """
        raise DynamoTableError(
            f"{self.__class__.__name__}.get_partition_key method is missing,"
            f" cannot get {self.partition_key_name} for {record}"
        )

    def get_sort_key(self, record: _RecordType) -> Any:
        """
        Override this method to get SK from a record.
        """
        raise DynamoTableError(
            f"{self.__class__.__name__}.get_sort_key method is missing,"
            f" cannot get {self.sort_key_name} for {record}"
        )

    def _get_partition_key(self, record: _RecordType) -> Any:
        if self.partition_key_name in record:
            return record[self.partition_key_name]

        return self.get_partition_key(record)

    def _get_sort_key(self, record: _RecordType) -> Any:
        if self.sort_key_name in record:
            return record[self.sort_key_name]

        return self.get_sort_key(record)

    def _convert_record(self, record: Union[_RecordType, Dict[str, Any]]) -> _RecordType:
        # pylint: disable=isinstance-second-argument-not-valid-type
        if self.record_class and not isinstance(record, self.record_class):
            # pylint: disable=not-callable
            return self.record_class(record)  # type: ignore

        return record  # type: ignore

    def get_table_status(self) -> Optional[str]:
        """
        Get table status from Dynamo.

        Returns:
            Status string or None.
        """
        try:
            response = self.client.describe_table(TableName=self.table.name)
        except self.client.exceptions.ResourceNotFoundException:
            return None

        return response["Table"]["TableStatus"]

    def delete_table(self) -> None:
        """
        Delete the table from DynamoDB.

        If table is creating, wait until it is created, then deletes it.
        If table is deleting or does not exist, does nothing.

        Example:

            ```python
            # UserTable is a subclass of a DynamoTable
            user_table = UserTable()

            # delete table
            UserTable.delete_table()

            # make sure that it is deleted
            user_table.wait_until_not_exists()
            ```
        """
        status = self.get_table_status()
        self._logger.debug(f"Table {self.table.name} status is {status}")

        if status is None:
            self._logger.debug(f"Table {self.table.name} does not exist, skipping deletion")
            return

        if status == "DELETING":
            self._logger.debug(f"Table {self.table.name} is deleting, skipping deletion")
            return

        if status == "CREATING":
            self._logger.debug(f"Table {self.table.name} is creating, waiting until created")
            self.wait_until_exists()

        self._logger.debug(f"Deleting {self.table.name}")
        self.table.delete()

    def create_table(self) -> Optional[CreateTableOutputTypeDef]:
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
        status = self.get_table_status()
        self._logger.debug(f"Table {self.table.name} status is {status}")

        if status == "DELETING":
            self._logger.debug(f"Table {self.table.name} is deleting, waiting until deleted")
            self.wait_until_not_exists()

        if status == "CREATING":
            self._logger.debug(f"Table {self.table.name} is creating, skipping")
            return None

        if status == "ACTIVE":
            self._logger.debug(f"Table {self.table.name} is active, skipping")
            return None

        global_secondary_indexes = [
            i.as_global_secondary_index() for i in self.global_secondary_indexes
        ]
        local_secondary_indexes = [
            i.as_local_secondary_index() for i in self.local_secondary_indexes
        ]

        extra_params: Dict[str, Any] = {}

        if global_secondary_indexes:
            extra_params["GlobalSecondaryIndexes"] = global_secondary_indexes
        if local_secondary_indexes:
            extra_params["LocalSecondaryIndexes"] = local_secondary_indexes

        if self.read_capacity_units and self.write_capacity_units:
            extra_params["ProvisionedThroughput"] = {
                "ReadCapacityUnits": self.read_capacity_units,
                "WriteCapacityUnits": self.write_capacity_units,
            }

        return self.client.create_table(
            AttributeDefinitions=self._attribute_definitions,
            TableName=self.table.name,
            KeySchema=self.primary_index.as_key_schema(),
            **extra_params,
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
            attribute_type = DynamoTableIndex.TYPES_MAP[attribute_definition["AttributeType"]]
            attribute_types[attribute_definition["AttributeName"]] = attribute_type
        return attribute_types

    # pylint: disable=no-self-use
    def normalize_record(self, record: _RecordType) -> _RecordType:
        """
        Modify record before upsert.

        Arguments:
            record -- Record for upsert.

        Returns:
            Normalized record.
        """
        return record

    def validate_record_attributes(self, record: _RecordType) -> None:
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
                    f"Attribute {attribute_name} has invalid type, {attribute_type} expected, got {type(value)}.",
                    data=record,
                )

    def _yield_from_query(
        self, query: DynamoQuery, data: Dict[str, Any], limit: Optional[int] = None
    ) -> Iterator[_RecordType]:
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

    def _get_keys_projection(self) -> Set[str]:
        if issubclass(self.record_class, DynamoDictClass):
            return self.table_keys | set(self.record_class.get_required_field_names())

        return self.table_keys

    def clear_table(
        self,
        partition_key: Optional[str] = None,
        partition_key_prefix: Optional[str] = None,
        sort_key: Optional[str] = None,
        sort_key_prefix: Optional[str] = None,
        index: DynamoTableIndex = primary_index,
        filter_expression: Optional[ConditionExpressionType] = None,
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
                projection=self._get_keys_projection(),
            )
        else:
            filter_expressions: List[ConditionExpression] = []
            data = {}
            if partition_key_prefix:
                filter_expressions.append(
                    ConditionExpression(self.partition_key_name, operator="begins_with")
                )
                data[self.partition_key_name] = partition_key_prefix
            if sort_key:
                filter_expressions.append(ConditionExpression(self.sort_key_name))
                data[self.sort_key_name] = sort_key
            if sort_key_prefix:
                filter_expressions.append(
                    ConditionExpression(self.sort_key_name, operator="begins_with")
                )
                data[self.sort_key_name] = sort_key_prefix

            if not filter_expressions:
                filter_expression = None
            else:
                filter_expression = filter_expressions[0]
                for part in filter_expressions[1:]:
                    filter_expression = filter_expression & part

            records = self.scan(
                filter_expression=filter_expression,
                data=data,
                projection=self._get_keys_projection(),
            )

        for records_chunk in chunkify(records, self.max_batch_size):
            existing_records = DataTable(record_class=self.record_class).add_record(*records_chunk)
            self.dynamo_query_class.build_batch_delete_item(logger=self._logger).table(
                table_keys=self.table_keys, table=self.table,
            ).execute(existing_records)

    def batch_get(self, data_table: DataTable[_RecordType]) -> DataTable[_RecordType]:
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
            return data_table.copy()
        get_data_table = DataTable(record_class=data_table.record_class)
        for record in data_table.get_records():
            record = self._convert_record(record)
            record = self.normalize_record(record)
            get_data_table.add_record(
                {
                    **record,
                    self.partition_key_name: self._get_partition_key(record),
                    self.sort_key_name: self._get_sort_key(record),
                }
            )

        results = (
            DynamoQuery.build_batch_get_item(logger=self._logger)
            .table(table_keys=self.table_keys, table=self.table)
            .execute(data_table=get_data_table)
        )
        return DataTable(record_class=self.record_class).add_table(results)

    def batch_delete(self, data_table: DataTable[_RecordType]) -> DataTable[_RecordType]:
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
            return DataTable(record_class=self.record_class)

        delete_data_table = DataTable(record_class=self.record_class)
        for record in data_table.get_records():
            record = self.normalize_record(self._convert_record(record))
            partition_key = self._get_partition_key(record)
            sort_key = self._get_sort_key(record)
            record.update({self.partition_key_name: partition_key, self.sort_key_name: sort_key})
            new_record = self._convert_record(record)
            delete_data_table.add_record(new_record)

        results = (
            DynamoQuery.build_batch_delete_item(logger=self._logger)
            .table(table_keys=self.table_keys, table=self.table)
            .execute(delete_data_table)
        )
        return DataTable(record_class=self.record_class).add_table(results)

    def batch_upsert(
        self, data_table: DataTable[_RecordType], set_if_not_exists_keys: Iterable[str] = (),
    ) -> DataTable[_RecordType]:
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
            return DataTable[_RecordType](record_class=self.record_class)

        set_if_not_exists = set(set_if_not_exists_keys)
        existing_records = self.batch_get(data_table)
        now = datetime.datetime.utcnow()
        now_str = now.isoformat()

        update_data_table = DataTable(record_class=self.record_class)
        for record_index, record in enumerate(existing_records.get_records()):
            updated_record = self._convert_record(data_table.get_record(record_index))
            preserve_keys_record: Dict[str, Any] = {}
            for key in set_if_not_exists:
                if key in record:
                    preserve_keys_record[key] = record[key]

            new_record = self._convert_record(
                {
                    **record,
                    **updated_record,
                    **preserve_keys_record,
                    "dt_created": record.get("dt_created") or now_str,
                    "dt_modified": now_str,
                }
            )

            normalized_record = self.normalize_record(new_record)
            self.validate_record_attributes(normalized_record)
            update_data_table.add_record(dict(normalized_record))

        results = (
            DynamoQuery.build_batch_update_item(logger=self._logger)
            .table(table_keys=self.table_keys, table=self.table,)
            .execute(update_data_table)
        )
        results.record_class = self.record_class
        return results

    def batch_get_records(self, records: Iterable[_RecordType]) -> Iterator[_RecordType]:
        """
        Get records as an iterator from DB.

        See `DynamoTable.batch_get`.

        Arguments:
            records -- Full or partial records data.

        Yields:
            Found or not found record data.
        """
        for records_chunk in chunkify(records, self.max_batch_size):
            get_data_table = DataTable(record_class=self.record_class).add_record(*records_chunk)
            result_data_table = self.batch_get(get_data_table)
            for record in result_data_table.get_records():
                yield self._convert_record(record)

    def batch_delete_records(self, records: Iterable[_RecordType]) -> None:
        """
        Delete records from DB.

        See `DynamoTable.batch_delete`.

        Arguments:
            records -- Full or partial records to delete.
        """
        for records_chunk in chunkify(records, self.max_batch_size):
            delete_data_table = DataTable[_RecordType](record_class=self.record_class).add_record(
                *records_chunk
            )
            self.batch_delete(delete_data_table)

    def batch_upsert_records(
        self, records: Iterable[_RecordType], set_if_not_exists_keys: Iterable[str] = (),
    ) -> None:
        """
        Upsert records to DB.

        See `DynamoTable.batch_upsert`.

        Arguments:
            records -- Full or partial records data.
            set_if_not_exists_keys -- List of keys to set only if they no do exist in DB.
        """
        for records_chunk in chunkify(records, self.max_batch_size):
            upsert_data_table = DataTable(record_class=self.record_class).add_record(*records_chunk)
            self.batch_upsert(upsert_data_table, set_if_not_exists_keys=set_if_not_exists_keys)

    def get_record(self, record: _RecordType) -> Optional[_RecordType]:
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
        record = self.normalize_record(self._convert_record(record))
        partition_key = self._get_partition_key(record)
        sort_key = self._get_sort_key(record)
        result = (
            self.dynamo_query_class.build_get_item(logger=self._logger)
            .table(table_keys=self.table_keys, table=self.table,)
            .execute_dict({self.partition_key_name: partition_key, self.sort_key_name: sort_key})
        )
        if set(result.get_set_column_names()).issubset(self.table_keys):
            return None

        return self._convert_record(result.get_record(0))

    def upsert_record(
        self,
        record: _RecordType,
        condition_expression: Optional[ConditionExpression] = None,
        set_if_not_exists_keys: Iterable[str] = (),
        extra_data: Dict[str, Any] = None,
    ) -> _RecordType:
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

        now = datetime.datetime.utcnow()
        now_str = now.isoformat()

        new_record = self._convert_record(
            {**record, **(extra_data or {}), "dt_modified": now_str, "dt_created": now_str,}
        )
        new_record = self.normalize_record(new_record)
        new_record.update(
            {
                self.partition_key_name: self._get_partition_key(new_record),
                self.sort_key_name: self._get_sort_key(new_record),
            }
        )

        update_keys = set(new_record.keys()) - self.table_keys - set_if_not_exists
        update_keys.add("dt_modified")
        result: DataTable[_RecordType] = (
            DynamoQuery.build_update_item(
                condition_expression=condition_expression, logger=self._logger,
            )
            .update(update=update_keys, set_if_not_exists=set_if_not_exists)
            .table(table_keys=self.table_keys, table=self.table,)
            .execute_dict(cast(Dict[str, Any], new_record))
        )
        return self._convert_record(result.get_record(0))

    def delete_record(
        self, record: _RecordType, condition_expression: Optional[ConditionExpression] = None,
    ) -> Optional[_RecordType]:
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
        record = self.normalize_record(self._convert_record(record))
        partition_key = self._get_partition_key(record)
        sort_key = self._get_sort_key(record)
        result: DataTable[_RecordType] = DynamoQuery.build_delete_item(
            condition_expression=condition_expression, logger=self._logger,
        ).table(table=self.table, table_keys=self.table_keys).execute_dict(
            {self.partition_key_name: partition_key, self.sort_key_name: sort_key},
        )
        if not result:
            return None
        return self._convert_record(result.get_record(0))

    def scan(
        self,
        filter_expression: Optional[ConditionExpressionType] = None,
        projection: Iterable[str] = tuple(),
        data: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> Iterator[_RecordType]:
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
        query = self.dynamo_query_class.build_scan(
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
            yield self._convert_record(record)

    def query(
        self,
        partition_key: Any,
        index: DynamoTableIndex = primary_index,
        sort_key: Optional[Any] = None,
        sort_key_prefix: Optional[str] = None,
        filter_expression: Optional[ConditionExpressionType] = None,
        scan_index_forward: bool = True,
        projection: Iterable[str] = tuple(),
        data: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> Iterator[_RecordType]:
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
        sort_key_operator: SortKeyOperatorTypeDef = "="
        partition_key_operator: PartitionKeyOperatorTypeDef = "="
        if sort_key_prefix is not None:
            sort_key_operator = "begins_with"
            sort_key = sort_key_prefix

        if partition_key is None:
            raise DynamoTableError("partition_key should be set.")

        key_condition_expression: ConditionExpressionType = ConditionExpression(
            index.partition_key_name, operator=partition_key_operator
        )
        if sort_key is not None and index.sort_key_name is not None:
            key_condition_expression = key_condition_expression & ConditionExpression(
                index.sort_key_name, operator=sort_key_operator,
            )
        query = self.dynamo_query_class.build_query(
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
            yield self._convert_record(record)

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

    def clear_records(self) -> None:
        """
        Delete all records managed by current table manager.

        Deletes only records with sort key starting with `sort_key_prefix`.
        """
        self.clear_table(sort_key_prefix=self.sort_key_prefix)
