"""
Helper for building Boto3 DynamoDB queries.
"""
import logging
from typing import Any, Dict, List, Optional, Set, cast

from dynamo_query.data_table import DataTable
from dynamo_query.dynamo_query_types import (
    BatchGetItemOutputTypeDef,
    BatchWriteItemOutputTypeDef,
    DeleteItemOutputTypeDef,
    DynamoDBClient,
    ExclusiveStartKey,
    ExpressionMap,
    FormatDict,
    GetItemOutputTypeDef,
    QueryOutputTypeDef,
    ScanOutputTypeDef,
    Table,
    TableKeys,
    UpdateItemOutputTypeDef,
)
from dynamo_query.enums import QueryType
from dynamo_query.expressions import BaseExpression, ExpressionError, Operator
from dynamo_query.json_tools import dumps
from dynamo_query.lazy_logger import LazyLogger
from dynamo_query.utils import ascii_string_generator, chunkify


class DynamoQueryError(Exception):
    """
    Main error for `dynamo_query.dynamo_query.DynamoQuery` class.
    """


class BaseDynamoQuery(LazyLogger):
    """
    Base class for building Boto3 DynamoDB queries. Use
    `dynamo_query.DynamoQuery` instead.

    ```python
    query = BaseDynamoQuery(
        query_type=QueryType.SCAN,
        expressions={
            BaseDynamoQuery.FILTER_EXPRESSION: ConditionExpression(
                'first_name',
                'last_name,
            ),
        }
        extra_params={}
        limit=5,
    )
    ```

    Arguments:
        query_type -- QueryType item.
        expressions -- Expressions for query.
        extra_params -- Any exptra params to pass to boto3 method.
        limit -- Limit of results for scan/query requests.
        exclusive_start_key -- Start key for scan/query requests.
        logger -- `logging.Logger` instance.
    """

    # Max size of one scan/query request.
    MAX_PAGE_SIZE = 1000

    # Max size of one batch_get/write/delete_item request.
    MAX_BATCH_SIZE = 25

    # Max size of scan/query requests.
    MAX_LIMIT = 10000000000

    FILTER_EXPRESSION = "FilterExpression"
    CONDITION_EXPRESSION = "ConditionExpression"
    UPDATE_EXPRESSION = "UpdateExpression"
    PROJECTION_EXPRESSION = "ProjectionExpression"
    KEY_CONDITION_EXPRESSION = "KeyConditionExpression"

    _expand_lists_expression_names = (
        FILTER_EXPRESSION,
        CONDITION_EXPRESSION,
    )

    _value_key_postfix = "__value"

    def __init__(
        self,
        query_type: QueryType,
        expressions: Dict[str, BaseExpression],
        extra_params: Dict[str, Any],
        limit: int = MAX_LIMIT,
        exclusive_start_key: Optional[ExclusiveStartKey] = None,
        logger: logging.Logger = None,
    ):
        self._lazy_logger = logger
        self._query_type = query_type
        self._expressions = expressions
        self._extra_params = extra_params
        self._limit = limit
        self._last_evaluated_key = exclusive_start_key
        self._was_executed = False
        self._raw_responses: List[Any] = []
        self._table_resource: Optional[Table] = None
        self._table_keys: Optional[TableKeys] = None

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} type={self._query_type.value}>"

    @property
    def table_resource(self) -> Table:
        if self._table_resource is None:
            raise DynamoQueryError("TableResource is not specified.")

        return self._table_resource

    @property
    def table_keys(self) -> TableKeys:
        if self._table_keys is None:
            raise DynamoQueryError("Table keys are not specified.")

        return self._table_keys

    @property
    def client(self) -> DynamoDBClient:
        return cast(DynamoDBClient, self.table_resource.meta.client)

    def was_executed(self) -> bool:
        """
        Whether query was excetuted at least once.

        Returns:
            True if query was executed.
        """
        return self._was_executed

    def has_more_results(self) -> bool:
        """
        Whether `scan` or `query` request with `limit` has more results to return.

        Returns:
            True if query has more results than returned or was not yet executed.
        """
        if not self.was_executed():
            return True

        return self._last_evaluated_key is not None

    @classmethod
    def _get_projection_dict(cls, expression_map: ExpressionMap) -> Dict[str, str]:
        expression_format_keys: Set[str] = set()
        for expression in expression_map.values():
            keys = expression.get_format_keys()
            expression_format_keys.update(keys)

        string_generator = ascii_string_generator(length=3)
        result = {}
        for key in sorted(expression_format_keys):
            result[f"#{next(string_generator)}"] = key

        return result

    @staticmethod
    def _split_values(values: str) -> Set[str]:
        result = set()
        for value in values.split(", "):
            if value.startswith(":"):
                result.add(value)

        return result

    @classmethod
    def _get_repr_format_dict(
        cls, projection_dict: Dict[str, str], data_dict: Dict[str, Any],
    ) -> FormatDict:
        result = {v: v for v in projection_dict.values()}
        for key, value in data_dict.items():
            result_key = f"{key}{cls._value_key_postfix}"
            result[result_key] = repr(value)

        return result

    @classmethod
    def _get_format_dict(
        cls,
        projection_dict: Dict[str, str],
        expression_map: ExpressionMap,
        data_dict: Dict[str, Any],
    ) -> FormatDict:
        result = {v: k for k, v in projection_dict.items()}
        expression_value_keys_map = {}
        for name, expression in expression_map.items():
            value_keys = expression.get_format_values()
            expression_value_keys_map[name] = value_keys

        string_generator = ascii_string_generator(length=3)
        for key, value in data_dict.items():
            for expression_name, value_keys in expression_value_keys_map.items():
                if key not in value_keys:
                    continue

                safe_key = next(string_generator)
                result_key = f"{key}{cls._value_key_postfix}"
                key_value = f":{safe_key}"
                expand_lists = expression_name in cls._expand_lists_expression_names

                if expand_lists and cls._is_set_like_value(value):
                    key_value = ", ".join([f":{safe_key}___{index}" for index in range(len(value))])
                result[result_key] = key_value

        return result

    @staticmethod
    def _is_set_like_value(value: Any) -> bool:
        return isinstance(value, (list, tuple, set))

    @classmethod
    def _get_expression_attribute_values(
        cls, format_dict: FormatDict, data_dict: Dict[str, Any],
    ) -> Dict[str, Any]:
        result = {}
        for key, value in data_dict.items():
            format_dict_key = f"{key}{cls._value_key_postfix}"
            if format_dict_key not in format_dict:
                continue

            required_values = cls._split_values(format_dict[format_dict_key])
            for required_value in required_values:
                if "___" in required_value:
                    index = int(required_value.rsplit("___")[-1])
                    result[required_value] = value[index]
                    continue

                result[required_value] = value

        return result

    @classmethod
    def _get_formatted_expressions(
        cls, expression_map: ExpressionMap, format_dict: FormatDict,
    ) -> Dict[str, str]:
        result = {}
        for name, expression in expression_map.items():
            result[name] = expression.render().format(**format_dict)

        return result

    def _validate_last_evaluated_key(self) -> None:
        if self._last_evaluated_key is None:
            return

        keys_set = set(self._last_evaluated_key.keys())
        if not self.table_keys.issubset(keys_set):
            raise DynamoQueryError(
                f"Expected ExclusiveStartKey to have {self.table_keys}" f" keys, got {keys_set}"
            )

    def _validate_required_value_keys(self, data_table: DataTable) -> None:
        for name, expression in self._expressions.items():
            required_value_keys = expression.get_format_values()
            for required_value_key in required_value_keys:
                if data_table.has_set_column(required_value_key):
                    continue

                if data_table.has_column(required_value_key):
                    raise DynamoQueryError(
                        f'Column "{required_value_key}"" has missing values in input data,'
                        f' but present in {name} = "{expression}"'
                    )

                raise DynamoQueryError(
                    f'Column "{required_value_key}" is missing in input data,'
                    f' but present in {name} = "{expression}"'
                )

    def _execute_method_query(self, data_table: DataTable) -> DataTable:
        self._validate_last_evaluated_key()
        self._validate_required_value_keys(data_table)

        for operator in self._expressions[self.KEY_CONDITION_EXPRESSION].get_operators():
            if operator not in (
                Operator.EQ.value,
                Operator.LT.value,
                Operator.GT.value,
                Operator.LTE.value,
                Operator.GTE.value,
                Operator.BETWEEN.value,
                Operator.BEGINS_WITH.value,
            ):
                raise DynamoQueryError(
                    f"{self.KEY_CONDITION_EXPRESSION} does not support operator" f' "{operator}".'
                )

        result = DataTable[Dict[str, Any]]()
        for record in data_table.get_records():
            result.add_table(self._execute_paginated_query(data=record))
        return result

    def _execute_method_scan(self, data_table: DataTable,) -> DataTable:
        self._validate_last_evaluated_key()
        self._validate_required_value_keys(data_table)

        result = DataTable[Dict[str, Any]]()
        for record in data_table.get_records():
            result.add_table(self._execute_paginated_query(data=record))
        return result

    def _execute_method_get_item(self, data_table: DataTable) -> DataTable:
        self._validate_data_table_has_table_keys(data_table)
        result = DataTable[Dict[str, Any]]()
        for record in data_table.get_records():
            key_data = {k: v for k, v in record.items() if k in self.table_keys}
            result_record = self._execute_item_query(key_data=key_data, item_data=record)
            if result_record is not None:
                record.update(result_record)
            result.add_record(record)
        return result

    def _validate_data_table_has_table_keys(self, data_table: DataTable) -> None:
        for table_key in self.table_keys:
            if data_table.has_set_column(table_key):
                continue

            if data_table.has_column(table_key):
                raise DynamoQueryError(
                    f'Column "{table_key}" has missing values in input data,'
                    f" but present in table keys {self.table_keys}"
                )

            raise DynamoQueryError(
                f'Column "{table_key}" is missing in input data,'
                f" but present in table keys {self.table_keys}"
            )

    def _execute_method_update_item(self, data_table: DataTable) -> DataTable:
        self._validate_data_table_has_table_keys(data_table)
        self._validate_required_value_keys(data_table)

        result = DataTable[Dict[str, Any]]()
        for record in data_table.get_records():
            if self.UPDATE_EXPRESSION not in self._expressions:
                raise DynamoQueryError(
                    f"{self} must have {self.UPDATE_EXPRESSION} or `update` method."
                )
            key_data = {k: v for k, v in record.items() if k in self.table_keys}
            result_record = self._execute_item_query(key_data=key_data, item_data=record,)
            if result_record is not None:
                result.add_record(result_record)
        return result

    def _execute_method_delete_item(self, data_table: DataTable,) -> DataTable:
        self._validate_data_table_has_table_keys(data_table)
        self._validate_required_value_keys(data_table)

        result = DataTable[Dict[str, Any]]()
        for record in data_table.get_records():
            key_data = {k: v for k, v in record.items() if k in self.table_keys}
            result_record = self._execute_item_query(key_data=key_data, item_data=record)
            if result_record is not None:
                result.add_record(result_record)
        return result

    def _execute_method_batch_get_item(self, data_table: DataTable) -> DataTable:
        self._validate_data_table_has_table_keys(data_table)

        record_chunks = chunkify(data_table.get_records(), self.MAX_BATCH_SIZE)
        table_name = self.table_resource.name
        response_table = DataTable[Dict[str, Any]]()
        for record_chunk in record_chunks:
            key_data_list = []
            for record in record_chunk:
                key_data = {k: v for k, v in record.items() if k in self.table_keys}
                key_data_list.append(key_data)
            request_items = {table_name: {"Keys": key_data_list}}
            response = self._batch_get_item(RequestItems=request_items, **self._extra_params,)
            if response.get("Responses", {}).get(table_name):
                response_table.add_record(*response["Responses"][table_name])

        result = DataTable[Dict[str, Any]]()
        for record in data_table.get_records():
            key_data = {k: v for k, v in record.items() if k in self.table_keys}
            response_records = response_table.filter_records(key_data).get_records()
            for response_record in response_records:
                record.update(response_record)
            result.add_record(record)

        return result

    def _execute_method_batch_update_item(self, data_table: DataTable) -> DataTable:
        self._validate_data_table_has_table_keys(data_table)

        record_chunks = chunkify(data_table.get_records(), self.MAX_BATCH_SIZE)
        table_name = self.table_resource.name
        for record_chunk in record_chunks:
            request_list = []
            for record in record_chunk:
                request_list.append({"PutRequest": {"Item": dict(record)}})
            request_items = {table_name: request_list}
            self._batch_write_item(
                RequestItems=request_items, **self._extra_params,
            )

        return data_table

    def _execute_method_batch_delete_item(self, data_table: DataTable) -> DataTable:
        self._validate_data_table_has_table_keys(data_table)

        record_chunks = chunkify(data_table.get_records(), self.MAX_BATCH_SIZE)
        table_name = self.table_resource.name
        for record_chunk in record_chunks:
            request_list = []
            for record in record_chunk:
                key_data = {k: v for k, v in record.items() if k in self.table_keys}
                request_item = {"DeleteRequest": {"Key": key_data}}
                if request_item not in request_list:
                    request_list.append(request_item)
            request_items = {table_name: request_list}
            self._batch_write_item(
                RequestItems=request_items, **self._extra_params,
            )

        return data_table

    def _batch_get_item(self, **kwargs: Any) -> BatchGetItemOutputTypeDef:
        response = self.client.batch_get_item(**kwargs)
        self._raw_responses.append(response)
        return response

    def _batch_write_item(self, **kwargs: Any) -> BatchWriteItemOutputTypeDef:
        response = self.client.batch_write_item(**kwargs)
        self._raw_responses.append(response)
        return response

    def _execute_get_item(self, **kwargs: Any) -> GetItemOutputTypeDef:
        response = self.table_resource.get_item(**kwargs)
        self._raw_responses.append(response)
        return response

    def _execute_update_item(self, **kwargs: Any) -> UpdateItemOutputTypeDef:
        response = self.table_resource.update_item(**kwargs)
        self._raw_responses.append(response)
        return response

    def _execute_delete_item(self, **kwargs: Any) -> DeleteItemOutputTypeDef:
        response = self.table_resource.delete_item(**kwargs)
        self._raw_responses.append(response)
        return response

    def _execute_query(self, **kwargs: Any) -> QueryOutputTypeDef:
        response = self.table_resource.query(**kwargs)
        self._raw_responses.append(response)
        return response

    def _execute_scan(self, **kwargs: Any) -> ScanOutputTypeDef:
        response = self.table_resource.scan(**kwargs)
        self._raw_responses.append(response)
        return response

    def _log_expressions(
        self,
        projection_dict: Dict[str, str],
        data_dict: Dict[str, Any],
        expression_map: ExpressionMap,
    ) -> None:
        repr_format_dict = self._get_repr_format_dict(
            projection_dict=projection_dict, data_dict=data_dict,
        )
        for name, expression in expression_map.items():
            self._logger.debug(f'Using {name} = "{expression.render().format(**repr_format_dict)}"')

    def _execute_item_query(
        self, key_data: Dict[str, Any], item_data: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        self._logger.debug(f"{self._query_type.value}_key_data = {dumps(key_data)}")
        expression_map = self._expressions
        if item_data:
            self._logger.debug(f"{self._query_type.value}_item_data = {dumps(item_data)}")
            for expression in self._expressions.values():
                try:
                    expression.validate_input_data(item_data)
                except ExpressionError as e:
                    raise DynamoQueryError(f"Invalid input data: {e}")

        projection_dict = self._get_projection_dict(expression_map)
        full_data = {
            **key_data,
            **item_data,
        }
        format_dict = self._get_format_dict(
            projection_dict=projection_dict, expression_map=expression_map, data_dict=full_data,
        )
        self._log_expressions(
            projection_dict=projection_dict, expression_map=expression_map, data_dict=full_data,
        )

        formatted_expressions = self._get_formatted_expressions(
            expression_map=expression_map, format_dict=format_dict,
        )
        expression_attribute_values = self._get_expression_attribute_values(
            format_dict=format_dict, data_dict=item_data,
        )

        extra_params = dict(self._extra_params)
        if projection_dict:
            extra_params["ExpressionAttributeNames"] = projection_dict
        if expression_attribute_values:
            extra_params["ExpressionAttributeValues"] = expression_attribute_values

        result: Optional[Dict[str, Any]] = None
        if self._query_type == QueryType.UPDATE_ITEM:
            update_response = self._execute_update_item(
                Key=key_data, **formatted_expressions, **extra_params,
            )
            self._was_executed = True
            result = update_response.get("Attributes")

        if self._query_type == QueryType.DELETE_ITEM:
            delete_response = self._execute_delete_item(
                Key=key_data, **formatted_expressions, **extra_params,
            )
            self._was_executed = True
            result = delete_response.get("Attributes")

        if self._query_type == QueryType.GET_ITEM:
            get_response = self._execute_get_item(
                Key=key_data, **formatted_expressions, **extra_params,
            )
            self._was_executed = True
            result = get_response.get("Item")

        return result

    def _execute_paginated_query(self, data: Dict[str, Any]) -> DataTable:
        self._logger.debug(f"query_data = {dumps(data)}")
        expression_map = self._expressions

        projection_dict = self._get_projection_dict(expression_map)
        format_dict = self._get_format_dict(
            projection_dict=projection_dict, expression_map=expression_map, data_dict=data,
        )
        self._log_expressions(
            projection_dict=projection_dict, expression_map=expression_map, data_dict=data,
        )

        last_page = False
        limit = self._limit
        expression_attribute_values = self._get_expression_attribute_values(
            format_dict=format_dict, data_dict=data,
        )
        formatted_expressions = self._get_formatted_expressions(
            expression_map=expression_map, format_dict=format_dict,
        )
        result = DataTable[Dict[str, Any]]()

        extra_params = dict(self._extra_params)
        if projection_dict:
            extra_params["ExpressionAttributeNames"] = projection_dict
        if expression_attribute_values:
            extra_params["ExpressionAttributeValues"] = expression_attribute_values

        while not last_page:
            page_limit = min(limit, self.MAX_PAGE_SIZE)
            page_params: Dict[str, Any] = dict(Limit=page_limit)
            if self._last_evaluated_key:
                page_params["ExclusiveStartKey"] = self._last_evaluated_key

            if self._query_type == QueryType.QUERY:
                response = self._execute_query(
                    **formatted_expressions, **extra_params, **page_params,
                )

                self._last_evaluated_key = response.get("LastEvaluatedKey")
                if not self._last_evaluated_key:
                    last_page = True

                result.add_record(*response.get("Items", []))

            if self._query_type == QueryType.SCAN:
                response = self._execute_scan(
                    **formatted_expressions, **extra_params, **page_params,
                )

                self._last_evaluated_key = response.get("LastEvaluatedKey")
                if not self._last_evaluated_key:
                    last_page = True

                result.add_record(*response.get("Items", []))

            self._was_executed = True

            limit = limit - page_limit
            if limit <= 0:
                last_page = True

        return result
