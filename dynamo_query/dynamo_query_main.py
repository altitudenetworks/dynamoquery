"""
Helper for building Boto3 DynamoDB queries.
"""
import logging
from typing import Any, Callable, Dict, Iterable, List, Optional, Type, TypeVar, Union

from dynamo_query.base_dynamo_query import BaseDynamoQuery, DynamoQueryError
from dynamo_query.data_table import DataTable
from dynamo_query.dynamo_query_types import (
    ExclusiveStartKey,
    ExpressionMap,
    RecordsType,
    ReturnConsumedCapacity,
    ReturnItemCollectionMetrics,
    ReturnValues,
    Table,
    TableKeys,
)
from dynamo_query.enums import QueryType
from dynamo_query.expressions import ConditionExpressionType, ProjectionExpression, UpdateExpression

__all__ = (
    "DynamoQuery",
    "DynamoQueryError",
)


_R = TypeVar("_R", bound="DynamoQuery")


class DynamoQuery(BaseDynamoQuery):
    """
    Helper for building Boto3 DynamoDB queries. See `BaseDynamoQuery`
    documentation as well.

    ```python
    query = DynamoQuery.build_scan(
        limit=5,
        filter_expression=ConditionExpression('first_name') & ('last_name', 'in'),
    ).projection(
        'first_name', 'last_name', 'age',
    )
    ...
    data_table = DataTable().add_record({
        'first_name': 'John',
        'last_name': ['Cena', 'Doe', 'Carmack'],
    })
    table_resource = DynamoConnect().resource.Table('people')
    result_data_table = query.execute(
        table_keys=('pk', ),
        table_resource=table_resource,
        data_table=data_table,
    )
    list(result_data_table.get_records())
    # [
    #     {
    #         'first_name': 'John',
    #         'last_name': 'Cena',
    #         'age': 42,
    #     },
    #     {
    #         'first_name': 'John',
    #         'last_name': 'Carmack',
    #         'age': 49,
    #     }
    # ]
    ```

    Attributes:
        MAX_LIMIT -- Max size of scan/query requests
        TABLE_KEYS -- Define in a subclass to set table keys automatically.
    """

    MAX_LIMIT = BaseDynamoQuery.MAX_LIMIT
    TABLE_KEYS: Optional[TableKeys] = None

    @classmethod
    def build_query(
        cls: Type[_R],
        key_condition_expression: ConditionExpressionType,
        index_name: Optional[str] = None,
        projection_expression: Optional[ProjectionExpression] = None,
        filter_expression: Optional[ConditionExpressionType] = None,
        limit: int = MAX_LIMIT,
        exclusive_start_key: Optional[ExclusiveStartKey] = None,
        consistent_read: bool = False,
        scan_index_forward: bool = True,
        logger: Optional[logging.Logger] = None,
    ) -> _R:
        """
        Build query for `table.query`.

        ```python
        query = DynamoQuery.build_query(
            key_condition_expression=ConditionExpression('first_name'),
            filter_expression=ConditionExpression('last_name', 'in'),
            index_name='gsi_first_name',
            limit=5,
            exclusive_start_key={'pk': '1'},
        ).projection(
            'first_name', 'last_name', 'age'
        )

        data_table = DataTable().add_record({
            'first_name': 'Test',
            'last_name': ['Last', 'Last2'],
        }, {
            'first_name': 'John',
            'last_name': ['Last', 'Last2'],
        })

        result_data_table = query.execute(
            table_resource=boto3_resource.Table('my_table'),
            table_keys=['pk'],
            data_table=data_table,
        )
        ```

        Arguments:
            key_condition_expression -- Format-ready KeyConditionExpression.
            filter_expression -- Format-ready FilterExpression.
            projection_expression -- Format-ready ProjectionExpression.
            limit -- Maximum number of results per input record.
            exclusive_start_key -- Key to start scan from.
            consistent_read -- `ConsistentRead` boto3 parameter.
            scan_index_forward -- Whether to scan index from the beginning.
            logger -- `logging.Logger` instance.

        Returns:
            `DynamoQuery` instance to execute.
        """
        expressions: ExpressionMap = {cls.KEY_CONDITION_EXPRESSION: key_condition_expression}
        if filter_expression:
            expressions[cls.FILTER_EXPRESSION] = filter_expression
        if projection_expression:
            expressions[cls.PROJECTION_EXPRESSION] = projection_expression

        extra_params: Dict[str, Any] = dict(
            ConsistentRead=consistent_read, ScanIndexForward=scan_index_forward,
        )
        if index_name is not None:
            extra_params["IndexName"] = index_name

        return cls(
            query_type=QueryType.QUERY,
            expressions=expressions,
            extra_params=extra_params,
            limit=limit,
            exclusive_start_key=exclusive_start_key,
            logger=logger,
        )

    @classmethod
    def build_scan(
        cls: Type[_R],
        filter_expression: Optional[ConditionExpressionType] = None,
        projection_expression: Optional[ProjectionExpression] = None,
        limit: int = MAX_LIMIT,
        exclusive_start_key: Optional[ExclusiveStartKey] = None,
        logger: Optional[logging.Logger] = None,
    ) -> _R:
        """
        Build query for `table.scan`.

        If `filter_expression` is not provided - it is constructed from input data.

        ```python
        query = DynamoQuery.build_scan(
            filter_expression=ConditionExpression('first_name') & ('last_name', 'in')
            limit=5,
            exclusive_start_key={'pk': '1'}
        ).projection(
            'first_name', 'last_name', 'age'
        )

        data_table = DataTable().add_record({
            'first_name': 'Test',
            'last_name': ['Last', 'Last2'],
        }, {
            'first_name': 'John',
            'last_name': ['Last', 'Last2'],
        })

        result_data_table = query.execute(
            table_resource=boto3_resource.Table('my_table'),
            table_keys=['pk'],
            data_table=data_table,
        )
        ```

        Arguments:
            filter_expression -- Format-ready FilterExpression.
            projection_expression -- Format-ready ProjectionExpression.
            limit -- Maximum number of results per input record.
            exclusive_start_key -- Key to start scan from.
            logger -- `logging.Logger` instance.

        Returns:
            `DynamoQuery` instance to execute.
        """
        expressions: ExpressionMap = dict()
        if filter_expression:
            expressions[cls.FILTER_EXPRESSION] = filter_expression
        if projection_expression:
            expressions[cls.PROJECTION_EXPRESSION] = projection_expression

        extra_params: Dict[str, Any] = dict()

        return cls(
            query_type=QueryType.SCAN,
            expressions=expressions,
            extra_params=extra_params,
            limit=limit,
            exclusive_start_key=exclusive_start_key,
            logger=logger,
        )

    @classmethod
    def build_get_item(
        cls: Type[_R],
        projection_expression: Optional[ProjectionExpression] = None,
        consistent_read: bool = False,
        return_consumed_capacity: ReturnConsumedCapacity = "NONE",
        logger: Optional[logging.Logger] = None,
    ) -> _R:
        """
        Build query for `table.get_item`.

        ```python
        query = DynamoQuery.build_get_item().projection(
            'first_name', 'last_name', 'age'
        )

        data_table = DataTable().add_record({
            'pk': 'key1',
        }, {
            'pk': 'key2',
        })

        result_data_table = query.execute(
            table_resource=boto3_resource.Table('my_table'),
            table_keys=['pk'],
            data_table=data_table,
        )
        ```

        Arguments:
            projection_expression -- Format-ready ProjectionExpression.
            consistent_read -- `ConsistentRead` boto3 parameter.
            return_consumed_capacity -- `ReturnConsumedCapacity` value.
            logger -- `logging.Logger` instance.

        Returns:
            `DynamoQuery` instance to execute.
        """
        expressions: ExpressionMap = dict()
        if projection_expression:
            expressions[cls.PROJECTION_EXPRESSION] = projection_expression

        extra_params: Dict[str, Any] = dict(
            ConsistentRead=consistent_read, ReturnConsumedCapacity=return_consumed_capacity,
        )

        return cls(
            query_type=QueryType.GET_ITEM,
            expressions=expressions,
            extra_params=extra_params,
            logger=logger,
        )

    @classmethod
    def build_update_item(
        cls: Type[_R],
        condition_expression: Optional[ConditionExpressionType] = None,
        update_expression: Optional[UpdateExpression] = None,
        return_consumed_capacity: ReturnConsumedCapacity = "NONE",
        return_item_collection_metrics: ReturnItemCollectionMetrics = "NONE",
        return_values: ReturnValues = "ALL_NEW",
        logger: Optional[logging.Logger] = None,
    ) -> _R:
        """
        Build query for `table.update_item`.

        If `update_expression` is not provided - it is constructed from input data.

        ```python
        query = DynamoQuery.build_update_item(
            filter_expression=ConditionExpression('first_name')
        ).update(
            'last_name', 'age',
        )

        data_table = DataTable().add_record({
            'pk': 'key1',
            'first_name': 'John',
            'age': 32,
        }, {
            'pk': 'key2',
            'first_name': 'Mike',
            'age': 19,
        })

        result_data_table = query.execute(
            table_resource=boto3_resource.Table('my_table'),
            table_keys=['pk'],
            data_table=data_table,
        )
        ```

        Arguments:
            condition_expression -- Format-ready ConditionExpression.
            update_expression -- Format-ready UpdateExpression.
            return_consumed_capacity -- `ReturnConsumedCapacity` value.
            return_item_collection_metrics -- `ReturnItemCollectionMetrics` value.
            return_values -- `ReturnValues` value.
            logger -- `logging.Logger` instance.

        Returns:
            `DynamoQuery` instance to execute.
        """
        expressions: ExpressionMap = dict()
        if condition_expression:
            expressions[cls.CONDITION_EXPRESSION] = condition_expression
        if update_expression:
            expressions[cls.UPDATE_EXPRESSION] = update_expression

        extra_params: Dict[str, Any] = dict(
            ReturnConsumedCapacity=return_consumed_capacity,
            ReturnItemCollectionMetrics=return_item_collection_metrics,
            ReturnValues=return_values,
        )

        return cls(
            query_type=QueryType.UPDATE_ITEM,
            expressions=expressions,
            extra_params=extra_params,
            logger=logger,
        )

    @classmethod
    def build_delete_item(
        cls: Type[_R],
        condition_expression: Optional[ConditionExpressionType] = None,
        return_consumed_capacity: ReturnConsumedCapacity = "NONE",
        return_item_collection_metrics: ReturnItemCollectionMetrics = "NONE",
        return_values: ReturnValues = "ALL_OLD",
        logger: Optional[logging.Logger] = None,
    ) -> _R:
        """
        Build query for `table.delete_item`.

        ```python
        query = DynamoQuery.build_delete_item(
            filter_expression=ConditionExpression('first_name')
        )

        data_table = DataTable().add_record({
            'pk': 'key1',
            'first_name': 'John',
        }, {
            'pk': 'key2',
            'first_name': 'Mike',
        })

        result_data_table = query.execute(
            table_resource=boto3_resource.Table('my_table'),
            table_keys=['pk'],
            data_table=data_table,
        )
        ```

        Arguments:
            condition_expression -- Format-ready ConditionExpression.
            return_consumed_capacity -- `ReturnConsumedCapacity` value.
            return_item_collection_metrics -- `ReturnItemCollectionMetrics` value.
            return_values -- `ReturnValues` value.
            logger -- `logging.Logger` instance.

        Returns:
            `DynamoQuery` instance to execute.
        """
        expressions: ExpressionMap = dict()
        if condition_expression:
            expressions[cls.CONDITION_EXPRESSION] = condition_expression

        extra_params: Dict[str, Any] = dict(
            ReturnConsumedCapacity=return_consumed_capacity,
            ReturnItemCollectionMetrics=return_item_collection_metrics,
            ReturnValues=return_values,
        )

        return cls(
            query_type=QueryType.DELETE_ITEM,
            expressions=expressions,
            extra_params=extra_params,
            logger=logger,
        )

    @classmethod
    def build_batch_get_item(
        cls: Type[_R],
        return_consumed_capacity: ReturnConsumedCapacity = "NONE",
        logger: Optional[logging.Logger] = None,
    ) -> _R:
        """
        Build query for `table.meta.client.batch_get_item`.

        ```python
        query = DynamoQuery.build_batch_get_item()
        data_table = DataTable().add_record({
            'pk': 'key1',
        }, {
            'pk': 'key2',
        })

        result_data_table = query.execute(
            table_resource=boto3_resource.Table('my_table'),
            table_keys=['pk'],
            data_table=data_table,
        )
        ```

        Arguments:
            return_consumed_capacity -- `ReturnConsumedCapacity` value.
            logger -- `logging.Logger` instance.

        Returns:
            `DynamoQuery` instance to execute.
        """
        extra_params = dict(ReturnConsumedCapacity=return_consumed_capacity)
        return cls(
            query_type=QueryType.BATCH_GET_ITEM,
            expressions={},
            extra_params=extra_params,
            logger=logger,
        )

    @classmethod
    def build_batch_update_item(
        cls: Type[_R],
        return_consumed_capacity: ReturnConsumedCapacity = "NONE",
        return_item_collection_metrics: ReturnItemCollectionMetrics = "NONE",
        logger: Optional[logging.Logger] = None,
    ) -> _R:
        """
        Build update query for `table.meta.client.batch_write_item`.

        ```python
        query = DynamoQuery.build_batch_update_item()
        data_table = DataTable().add_record({
            'pk': 'key1',
            'first_name': 'John',
        }, {
            'pk': 'key2',
            'first_name': 'Smith',
        })

        result_data_table = query.execute(
            table_resource=boto3_resource.Table('my_table'),
            table_keys=['pk'],
            data_table=data_table,
        )
        ```

        Arguments:
            return_consumed_capacity -- `ReturnConsumedCapacity` value.
            return_item_collection_metrics -- `ReturnItemCollectionMetrics` value.
            logger -- `logging.Logger` instance.

        Returns:
            `DynamoQuery` instance to execute.
        """
        extra_params = dict(
            ReturnConsumedCapacity=return_consumed_capacity,
            ReturnItemCollectionMetrics=return_item_collection_metrics,
        )
        return cls(
            query_type=QueryType.BATCH_UPDATE_ITEM,
            expressions={},
            extra_params=extra_params,
            logger=logger,
        )

    @classmethod
    def build_batch_delete_item(
        cls: Type[_R],
        return_consumed_capacity: ReturnConsumedCapacity = "NONE",
        return_item_collection_metrics: ReturnItemCollectionMetrics = "NONE",
        logger: Optional[logging.Logger] = None,
    ) -> _R:
        """
        Build delete query for `table.meta.client.batch_write_item`.

        ```python
        query = DynamoQuery.build_batch_delete_item()
        data_table = DataTable().add_record({
            'pk': 'key1',
        }, {
            'pk': 'key2',
        })

        result_data_table = query.execute(
            table_resource=boto3_resource.Table('my_table'),
            table_keys=['pk'],
            data_table=data_table,
        )
        ```

        Arguments:
            return_consumed_capacity -- `ReturnConsumedCapacity` value.
            return_item_collection_metrics -- `ReturnItemCollectionMetrics` value.
            logger -- `logging.Logger` instance.

        Returns:
            `DynamoQuery` instance to execute.
        """
        extra_params = dict(
            ReturnConsumedCapacity=return_consumed_capacity,
            ReturnItemCollectionMetrics=return_item_collection_metrics,
        )
        return cls(
            query_type=QueryType.BATCH_DELETE_ITEM,
            expressions={},
            extra_params=extra_params,
            logger=logger,
        )

    def table(
        self: _R, table: Optional[Table], table_keys: Optional[TableKeys] = TABLE_KEYS,
    ) -> _R:
        """
        Set table resource and table keys.

        Arguments:
            table -- `boto3_resource.Table('my_table')`.
            table_keys -- Primary and sort keys for table.
        """
        self._table_resource = table
        self._table_keys = set(table_keys) if table_keys else self.TABLE_KEYS
        return self

    def execute(
        self,
        data_table: Union[DataTable, RecordsType],
        table: Optional[Table] = None,
        table_keys: Optional[TableKeys] = TABLE_KEYS,
    ) -> DataTable:
        """
        Execute a query and get results. To get raw AWS responses, use
        `query.get_raw_responses()` after this method. To get `LastEvaluatedKey`, use
        `query.get_last_evaluated_key()` after this method.

        If `table_keys` were not provided, method gets them from table schema. It is
        slow, so it is better to pass them explicitly.

        ```python
        input_data_table = DataTable()
        input_data_table.add_record({
            'name': 'John',
        }, {
            'name': 'Mike',
        })
        results = DynamoQuery.build_scan(
            filter_expression=ConditionExpression('name'),
        ).execute(
            table_keys=['pk'],
            table=table_resource,
            data_table=input_data_table,
        )
        ```

        Arguments:
            table -- `boto3_resource.Table('my_table')`.
            data_table -- `DataTable` with input data.
            table_keys -- Primary and sort keys for table.

        Returns:
            A `DataTable` with query results.
        """
        if not isinstance(data_table, DataTable):
            data_table = DataTable().add_record(*data_table)

        if not data_table.is_normalized():
            raise DynamoQueryError("Input DataTable is not normalized.")

        self.table(
            table=table or self.table_resource, table_keys=table_keys or self._table_keys,
        )

        self._logger.debug(f"Execute {self._query_type.value} on {self.table_resource.name}")

        if self._table_keys is None:
            self._logger.warning(
                "Table keys were not set, use `table_keys` argument, getting from schema."
            )
            self._table_keys = self.get_table_keys(self.table_resource)
            self._logger.debug(f"Got table keys {set(self._table_keys)}")

        self._raw_responses = []

        method_map: Dict[QueryType, Callable[[DataTable], DataTable]] = {
            QueryType.QUERY: self._execute_method_query,
            QueryType.SCAN: self._execute_method_scan,
            QueryType.GET_ITEM: self._execute_method_get_item,
            QueryType.UPDATE_ITEM: self._execute_method_update_item,
            QueryType.DELETE_ITEM: self._execute_method_delete_item,
            QueryType.BATCH_GET_ITEM: self._execute_method_batch_get_item,
            QueryType.BATCH_UPDATE_ITEM: self._execute_method_batch_update_item,
            QueryType.BATCH_DELETE_ITEM: self._execute_method_batch_delete_item,
        }
        return method_map[self._query_type](data_table)

    def execute_dict(
        self,
        data: Optional[Dict[str, Any]] = None,
        table: Optional[Table] = None,
        table_keys: Optional[TableKeys] = TABLE_KEYS,
    ) -> DataTable:
        """
        Execute a query for a single record and get results. See `DynamoQuery.execute` method.

        ```python
        search_data = {
            'name': 'John',
        }
        results = DynamoQuery.build_scan(
            filter_expression=ConditionExpression('name'),
        ).execute_dict(
            table_keys=['pk'],
            table=table_resource,
            data=search_data,
        )
        ```

        Arguments:
            table -- `boto3_resource.Table('my_table')`.
            data -- Record of a `DataTable` or a regular `dict`.
            table_keys -- Primary and sort keys for table.

        Returns:
            A `DataTable` with query results.
        """
        self.table(
            table=table or self.table_resource, table_keys=table_keys or self._table_keys,
        )
        return self.execute(data_table=[data or {"dummy": True}])

    def get_last_evaluated_key(self) -> Optional[ExclusiveStartKey]:
        """
        Get LastEvaluatedKey from the last execution.

        ```python
        query = DynamoQuery.build_scan(limit=5)
        results = query.execute()

        # if you use the same query it remembers LastEvaluatedKey, so you get the next page
        # on the next execution

        results_page2 = query.execute()

        # to continue from the same place later, save `LastEvaluatedKey`

        start_key = query.get_last_evaluated_key()

        query2 = DynamoQuery.build_scan(
            limit=5,
            exclusive_start_key=start_key,
        )
        results_page3 = query.execute()
        ```

        Returns:
            A dict that can be used in `ExclusiveStartKey` parameter.
        """
        return self._last_evaluated_key

    def reset_start_key(self: _R) -> _R:
        """
        Set paginated query to the start.
        """
        self._last_evaluated_key = None
        return self

    def get_raw_responses(self) -> List[Dict]:
        """
        Get raw AWS responses from the last execution. Use flags `ReturnConsumedCapacity` and
        `ReturnItemCollectionMetrics` to get additional metrics. Also `Count` and `ScannedCount`
        fields might be interesting.

        Returns:
            A list of AWS responses.
        """
        return self._raw_responses

    @staticmethod
    def get_table_keys(table: Table) -> TableKeys:
        """
        Get table keys from schema.

        ```python
        table = boto3.resource('dynamodb').Table('my_table')
        table_keys = DynamoQuery.get_table_keys()
        table_keys # ['pk', 'sk']
        ```

        Arguments:
            table -- `boto3_resource.Table('my_table')`.

        Returns:
            A list of table keys.
        """
        key_schema = table.key_schema
        result: TableKeys = set()
        for key_data in key_schema:
            if "AttributeName" in key_data:
                result.add(key_data["AttributeName"])

        return result

    def projection(self: _R, *fields: str) -> _R:
        """
        Django ORM-like shortcut for adding `ProjectionExpression`

        ```python
        query = DynamoQuery.build_update()
        query.projection(update=['field1', 'field2')

        # lines above are equivalent to

        query = DynamoQuery.build_update(
            projection_expression=ProjectionExpression('field1', 'field2')
        )
        ```

        Arguments:
            fields - A list of fields to use as ProjectionExpression keys

        Returns:
            Itself, so this method can be chained.
        """
        if self._query_type not in (QueryType.QUERY, QueryType.SCAN, QueryType.GET_ITEM,):
            raise DynamoQueryError(f"{self} does not support ProjectionExpression")
        self._expressions[self.PROJECTION_EXPRESSION] = ProjectionExpression(*fields)
        return self

    def limit(self: _R, limit: int) -> _R:
        """
        Limit results for `scan` or `query` method.

        ```python
        query = DynamoQuery.scan()
        query.limit(10)
        ```

        Arguments:
            limit - Number of max entries.

        Returns:
            Itself, so this method can be chained.
        """
        if self._query_type not in (QueryType.QUERY, QueryType.SCAN):
            raise DynamoQueryError(f"{self} does not support Limit")

        self._limit = limit
        return self

    def update(
        self: _R,
        *args: str,
        update: Iterable[str] = tuple(),
        set_if_not_exists: Iterable[str] = tuple(),
        add: Iterable[str] = tuple(),
        delete: Iterable[str] = tuple(),
        remove: Iterable[str] = tuple(),
    ) -> _R:
        """
        Shortcut for adding `UpdateExpression`.

        ```python
        query = DynamoQuery.build_update()
        query.update(update=['field1'], add=['my_list'])

        # lines above are equivalent to

        query = DynamoQuery.build_update(
            update_expression=UpdateExpression(update=['field1'], add=['my_list'])
        )
        ```

        Arguments:
            args -- Keys to use SET expression, use to update values.
            update -- Keys to use SET expression, use to update values.
            set_if_not_exists -- Keys to use SET expression, use to add new keys.
            add -- Keys to use ADD expression, use to extend lists.
            delete -- Keys to use DELETE expression, use to subtract lists.
            remove -- Keys to use REMOVE expression, use to remove values.

        Returns:
            Itself, so this method can be chained.
        """
        if self._query_type is not QueryType.UPDATE_ITEM:
            raise DynamoQueryError(f"{self} does not support UpdateExpression")

        self._expressions[self.UPDATE_EXPRESSION] = UpdateExpression(
            *args,
            update=update,
            set_if_not_exists=set_if_not_exists,
            add=add,
            delete=delete,
            remove=remove,
        )
        return self
