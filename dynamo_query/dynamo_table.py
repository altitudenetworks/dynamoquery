from typing import (
    Optional,
    Dict,
    Any,
    Iterator,
    Iterable,
    Set,
    TypeVar,
    Generic,
    Mapping,
    Union,
    cast,
)
import logging
import datetime
from abc import abstractproperty, abstractmethod

from typing_extensions import Literal

from dynamo_query.dynamo_query import DynamoQuery
from dynamo_query.expressions import ConditionExpression, ConditionExpressionGroup
from dynamo_query.data_table import DataTable
from dynamo_query.dynamo_table_index import DynamoTableIndex
from dynamo_query.types import Table, DynamoDBClient


__all__ = ("DynamoTable",)

DynamoRecord = TypeVar("DynamoRecord", bound=Mapping[str, Any])


class DynamoTable(Generic[DynamoRecord]):
    partition_key_name = "pk"
    sort_key_name = "sk"
    table_keys: Set[str] = {partition_key_name, sort_key_name}
    global_secondary_indexes: Iterable[DynamoTableIndex] = []
    local_secondary_indexes: Iterable[DynamoTableIndex] = []
    sort_key_prefix: Optional[str] = None

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
    def _get_partition_key(self, record: DynamoRecord) -> Any:
        """
        Override this method to get PK from a record.
        """

    @abstractmethod
    def _get_sort_key(self, record: DynamoRecord) -> Any:
        """
        Override this method to get SK from a record.
        """

    @property
    def _logger(self) -> logging.Logger:
        if self._lazy_logger is None:
            self._lazy_logger = logging.Logger(__name__)

        return self._lazy_logger

    def get_partition_key(self, record: DynamoRecord) -> Any:
        if self.partition_key_name in record:
            return record[self.partition_key_name]

        return self._get_partition_key(record)

    def get_sort_key(self, record: DynamoRecord) -> Any:
        if self.sort_key_name in record:
            return record[self.sort_key_name]

        return self._get_sort_key(record)

    def create_table(self) -> None:
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
        """
        Yield records for query.

        Arguments:
            query -- DynamoQuery.build_query() instance.
            data -- Query data.

        Yields:
            A DataTable with matching results.
        """
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
        Get items by table keys.

        `data_table` must have `pk` and `sk` column with set values.

        Arguments:
            data_table -- Request data table.

        Returns:
            DataTable with existing records.
        """
        if not data_table:
            return DataTable()
        get_data_table = DataTable[DynamoRecord]()
        for record in data_table.get_records():
            partition_key = self.get_partition_key(record)
            sort_key = self.get_sort_key(record)
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
        Delete items by table keys.

        `data_table` must have `pk` and `sk` columns with set values.

        Arguments:
            data_table -- Request data table.

        Returns:
            DataTable with deleted records.
        """
        if not data_table:
            return DataTable()

        delete_data_table = DataTable[DynamoRecord]()
        for record in data_table.get_records():
            partition_key = self.get_partition_key(record)
            sort_key = record.get(self.sort_key_name) or self.get_sort_key(record)
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
        Upsert DataTable to DB.

        Arguments:
            data_table -- DataTable with set `pk` and `sk`.

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

        Arguments:
            record -- Record with required fields for sort and partition keys.

        Returns:
            A dict with record data or None.
        """
        partition_key = self.get_partition_key(record)
        sort_key = self.get_sort_key(record)
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

        Arguments:
            record -- Record to insert/update.
            condition_expression -- Condition for update.
            extra_data -- Data for query.

        Returns:
            A dict with updated record data.
        """
        update_keys = set(record.keys()) - self.table_keys
        partition_key = self.get_partition_key(record)
        sort_key = self.get_sort_key(record)
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

        Arguments:
            record -- Record with required fields for sort and partition keys.
            condition_expression -- Condition for delete.

        Returns:
            A dict with record data or None.
        """
        partition_key = self.get_partition_key(record)
        sort_key = self.get_sort_key(record)
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
        Yield records from a table.

        Arguments:
            filter_expression -- Query filter expression.
            scan_index_forward -- Whether to scan index from the beginning.
            projection -- Record fields to return, by default returns all fields.
            limit -- Max number of results.
        """
        query = DynamoQuery.build_scan(filter_expression=filter_expression)

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
        Yield results from a query using index.

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

        if projection:
            query.projection(*projection)

        query_data = index.get_query_data(partition_key, sort_key)
        if data:
            query_data.update(data)

        for record in self._yield_from_query(query, data=query_data, limit=limit):
            yield record
