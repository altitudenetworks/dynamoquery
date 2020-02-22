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
    TypeVar,
    Union,
    cast,
)

from typing_extensions import Literal

from dynamo_query.data_table import DataTable
from dynamo_query.dynamo_query import DynamoQuery
from dynamo_query.dynamo_table_index import DynamoTableIndex
from dynamo_query.expressions import ConditionExpression, ConditionExpressionGroup
from dynamo_query.types import DynamoDBClient, Table

__all__ = ("DynamoTable",)

DynamoRecord = TypeVar("DynamoRecord", bound=Mapping[str, Any])


class DynamoTable(Generic[DynamoRecord]):
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

    @abstractproperty
    def table(self) -> Table:
        """
        Override this method to get DynamoDB Table resource.
        """

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

    @property
    def _logger(self) -> logging.Logger:
        if self._lazy_logger is None:
            self._lazy_logger = logging.Logger(__name__)

        return self._lazy_logger

    def _get_partition_key(self, record: DynamoRecord) -> Any:
        if self.partition_key_name in record:
            return record[self.partition_key_name]

        return self.get_partition_key(record)

    def _get_sort_key(self, record: DynamoRecord) -> Any:
        if self.sort_key_name in record:
            return record[self.sort_key_name]

        return self.get_sort_key(record)

    def create_table(self) -> None:
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
        client: DynamoDBClient = self.table.meta.client
        client.create_table(
            AttributeDefinitions=self.primary_index.as_attribute_definitions(),
            TableName=self.table.name,
            KeySchema=self.primary_index.as_key_schema(),
            GlobalSecondaryIndexes=global_secondary_indexes,
            LocalSecondaryIndexes=local_secondary_indexes,
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

    def clear_table(self, partition_key: Optional[str]) -> None:
        """
        Remove all records.

        If `partition_key` is None - deletes all records.

        Example:

            ```python
            # UserTable is a subclass of a DynamoTable
            user_table = UserTable()

            # delete all records that have PK = `emails`
            user_table.clear_table("emails")

            # delete all records
            user_table.clear_table(None)
            ```

        Arguments:
            partition_key -- Partition key value.
        """
        self._logger.info(
            f"Clearing table with PK={partition_key} and SK_prefix={self.sort_key_prefix}."
        )
        self._clear_table(
            partition_key=partition_key, sort_key_prefix=self.sort_key_prefix
        )

    def _clear_table(
        self,
        partition_key: Optional[str],
        sort_key: Optional[str] = None,
        sort_key_prefix: Optional[str] = None,
        index: DynamoTableIndex = primary_index,
        filter_expression: Optional[ConditionExpression] = None,
        limit: Optional[int] = None,
    ) -> None:
        """
        Delete results of a query from DB.

        If `partition_key` is None - deletes all records.

        Arguments:
            partition_key -- Partition key value.
            sort_key -- Sort key value.
            sort_key_prefix -- Sort key prefix.
            index -- DynamoTableIndex instance, primary index is used if not provided.
            filter_expression -- Query filter expression.
            limit -- Max number of results.
        """
        if partition_key is None:
            records = self.scan(projection=self.table_keys)
        else:
            records = self.query(
                partition_key=partition_key,
                index=index,
                sort_key=sort_key,
                sort_key_prefix=sort_key_prefix,
                filter_expression=filter_expression,
                limit=limit,
                projection=self.table_keys,
            )

        existing_records = DataTable[DynamoRecord]().add_record(*records)

        if not existing_records:
            return

        DynamoQuery.build_batch_delete_item().table(
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

        results: DataTable[DynamoRecord] = DynamoQuery.build_batch_get_item().table(
            table_keys=self.table_keys, table=self.table,
        ).execute(data_table=get_data_table,)
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

        results: DataTable[DynamoRecord] = DynamoQuery.build_batch_delete_item().table(
            table_keys=self.table_keys, table=self.table,
        ).execute(delete_data_table)
        return results

    def batch_upsert(
        self, data_table: DataTable[DynamoRecord]
    ) -> DataTable[DynamoRecord]:
        """
        Upsert multuple records as a DataTable to DB.

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

        Returns:
            A DataTable with upserted results.
        """
        if not data_table:
            return DataTable[DynamoRecord]()

        existing_records = self.batch_get(data_table)
        now = datetime.datetime.utcnow()

        update_data_table: DataTable[DynamoRecord] = DataTable()
        for record_index, record in enumerate(existing_records.get_records()):
            updated_record = data_table.get_record(record_index)
            new_record = cast(
                DynamoRecord,
                {
                    **record,
                    **updated_record,
                    "dt_created": record.get("dt_created", now),
                    "dt_modified": now,
                },
            )
            update_data_table.add_record(new_record)

        results: DataTable[DynamoRecord] = DynamoQuery.build_batch_update_item().table(
            table_keys=self.table_keys, table=self.table,
        ).execute(update_data_table)
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
            DynamoQuery.build_get_item()
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
        extra_data: Dict[str, Any] = None,
    ) -> DynamoRecord:
        """
        Upsert Record to DB.

        `record` must have all fields to calculate table keys.

        Example:

            ```python
            # UserTable is a subclass of a DynamoTable
            user_table = UserTable()

            # we should provide table keys or fields to calculate them
            # in our case, PK is calculated from `email` field.
            deleted_record = user_table.delete_record({
                "email": "newuser@gmail.com",
                "name": "Somebody Oncetoldme"
                "age": 23,
            })

            if deleted_record is None:
                # no record found, so nothing was deleted
                pass
            else:
                # print deleted record
                print(user_record)
            ```

        Arguments:
            record -- Record to insert/update.
            condition_expression -- Condition for update.
            extra_data -- Data for query.

        Returns:
            A dict with updated record data.
        """
        update_keys = set(record.keys()) - self.table_keys
        partition_key = self._get_partition_key(record)
        sort_key = self._get_sort_key(record)
        result: DataTable[DynamoRecord] = (
            DynamoQuery.build_update_item(condition_expression=condition_expression)
            .update(*update_keys)
            .table(table_keys=self.table_keys, table=self.table,)
            .execute_dict(
                {
                    self.partition_key_name: partition_key,
                    self.sort_key_name: sort_key,
                    **record,
                    **(extra_data or {}),
                }
            )
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
            condition_expression=condition_expression,
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
        query = DynamoQuery.build_scan(filter_expression=filter_expression)
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
            sort_key_prefix -- Sort key prefix.
            filter_expression -- Query filter expression.
            scan_index_forward -- Whether to scan index from the beginning.
            projection -- Record fields to return, by default returns all fields.
            limit -- Max number of results.

        Yields:
            Matching record.
        """
        sort_key_operator: Literal["=", "begins_with"] = "="
        if sort_key_prefix is not None:
            sort_key_operator = "begins_with"
            sort_key = sort_key_prefix

        key_condition_expression: Union[
            ConditionExpression, ConditionExpressionGroup
        ] = ConditionExpression(index.partition_key_name)
        if sort_key is not None and index.sort_key_name is not None:
            key_condition_expression = key_condition_expression & ConditionExpression(
                index.sort_key_name, operator=sort_key_operator,
            )
        query = DynamoQuery.build_query(
            index_name=index.name,
            key_condition_expression=key_condition_expression,
            filter_expression=filter_expression,
            scan_index_forward=scan_index_forward,
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
