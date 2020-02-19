from unittest.mock import MagicMock, ANY

import pytest

from dynamo_query.dynamo_query import DynamoQuery, DynamoQueryError
from dynamo_query.data_table import DataTable
from dynamo_query.expressions import ConditionExpression


class TestDynamoQuery:
    @staticmethod
    def test_methods() -> None:
        filter_expression_mock = MagicMock()
        projection_expression_mock = MagicMock()
        table_resource_mock = MagicMock()
        query = DynamoQuery.build_query(
            key_condition_expression=ConditionExpression("key"),
            index_name="my_index",
            filter_expression=filter_expression_mock,
            projection_expression=projection_expression_mock,
            limit=100,
        )

        with pytest.raises(DynamoQueryError):
            _ = query.table_resource

        with pytest.raises(DynamoQueryError):
            _ = query.table_keys

        query.table(table=table_resource_mock)
        assert str(query) == "<DynamoQuery type=query>"
        assert query.table_resource == table_resource_mock
        assert not query.was_executed()
        assert query.has_more_results()

        query.execute_dict({"key": "value"})
        assert query.was_executed()
        assert query.has_more_results()
        assert query.get_last_evaluated_key() == table_resource_mock.query().get()
        assert query.get_raw_responses() == [table_resource_mock.query()]

        table_resource_mock.key_schema = [
            {"AttributeName": "key"},
            {"NotKey": "not_key"},
        ]
        assert query.get_table_keys(table_resource_mock) == ["key"]

    @staticmethod
    def test_expression_methods() -> None:
        query = DynamoQuery.build_batch_get_item()

        with pytest.raises(DynamoQueryError):
            query.update("key")

        with pytest.raises(DynamoQueryError):
            query.projection("key")

    @staticmethod
    def test_errors() -> None:
        filter_expression_mock = MagicMock()
        projection_expression_mock = MagicMock()
        table_resource_mock = MagicMock()
        query = DynamoQuery.build_query(
            key_condition_expression=ConditionExpression("key", "contains"),
            index_name="my_index",
            filter_expression=filter_expression_mock,
            projection_expression=projection_expression_mock,
            limit=100,
        ).table(table=table_resource_mock, table_keys=("pk", "sk"))

        with pytest.raises(DynamoQueryError):
            query.execute_dict({"key": "value"})

        query = DynamoQuery.build_query(
            key_condition_expression=ConditionExpression("key"),
            index_name="my_index",
            filter_expression=filter_expression_mock,
            projection_expression=projection_expression_mock,
            limit=100,
        ).table(table=table_resource_mock, table_keys=("pk", "sk"))

        with pytest.raises(DynamoQueryError):
            query.execute_dict({"key1": "value"})

        with pytest.raises(DynamoQueryError):
            query.execute(DataTable.create({"a": [1, 2], "b": [3]}))

    @staticmethod
    def test_query() -> None:
        key_condition_expression_mock = MagicMock()
        filter_expression_mock = MagicMock()
        projection_expression_mock = MagicMock()
        table_resource_mock = MagicMock()
        query = (
            DynamoQuery.build_query(
                key_condition_expression=key_condition_expression_mock,
                index_name="my_index",
                filter_expression=filter_expression_mock,
                projection_expression=projection_expression_mock,
                limit=100,
            )
            .table(table=table_resource_mock, table_keys=("pk", "sk"))
            .projection("test")
        )
        result = query.execute_dict({"key": "value"})
        table_resource_mock.query.assert_called_with(
            ConsistentRead=False,
            ExpressionAttributeNames={"#aaa": "test"},
            FilterExpression=filter_expression_mock.render().format(),
            IndexName="my_index",
            KeyConditionExpression=key_condition_expression_mock.render().format(),
            Limit=100,
            ProjectionExpression="#aaa",
            ScanIndexForward=True,
        )
        assert list(result.get_records()) == []
        query.reset_start_key().execute(
            DataTable.create().add_record({"key": "value"}, {"key": "value2"})
        )
        table_resource_mock.query.assert_called_with(
            ConsistentRead=False,
            ExclusiveStartKey=ANY,
            ExpressionAttributeNames={"#aaa": "test"},
            FilterExpression=filter_expression_mock.render().format(),
            IndexName="my_index",
            KeyConditionExpression=key_condition_expression_mock.render().format(),
            Limit=100,
            ProjectionExpression="#aaa",
            ScanIndexForward=True,
        )

    @staticmethod
    def test_scan() -> None:
        filter_expression_mock = MagicMock()
        projection_expression_mock = MagicMock()
        table_resource_mock = MagicMock()
        query = (
            DynamoQuery.build_scan(
                filter_expression=filter_expression_mock,
                projection_expression=projection_expression_mock,
                limit=100,
            )
            .table(table=table_resource_mock, table_keys=("pk", "sk"))
            .projection("test")
        )
        result = query.execute_dict({"key": "value"})
        table_resource_mock.scan.assert_called_with(
            ExpressionAttributeNames={"#aaa": "test"},
            FilterExpression=filter_expression_mock.render().format(),
            Limit=100,
            ProjectionExpression="#aaa",
        )
        assert list(result.get_records()) == []

    @staticmethod
    def test_get_item() -> None:
        projection_expression_mock = MagicMock()
        table_resource_mock = MagicMock()
        query = (
            DynamoQuery.build_get_item(projection_expression=projection_expression_mock)
            .table(table=table_resource_mock, table_keys=("pk", "sk"))
            .projection("test")
        )
        result = query.execute_dict({"pk": "value", "sk": "value"})
        table_resource_mock.get_item.assert_called_with(
            ConsistentRead=False,
            ExpressionAttributeNames={"#aaa": "test"},
            Key={"pk": "value", "sk": "value"},
            ProjectionExpression="#aaa",
            ReturnConsumedCapacity="NONE",
        )
        assert list(result.get_records()) == [{"pk": "value", "sk": "value"}]

    @staticmethod
    def test_update_item() -> None:
        condition_expression_mock = MagicMock()
        update_expression_mock = MagicMock()
        table_resource_mock = MagicMock()
        query = (
            DynamoQuery.build_update_item(
                condition_expression=condition_expression_mock,
                update_expression=update_expression_mock,
            )
            .table(table=table_resource_mock, table_keys=("pk", "sk"))
            .update("test")
        )
        result = query.execute_dict({"pk": "value", "sk": "value", "test": "data"})
        table_resource_mock.update_item.assert_called_with(
            ConditionExpression=condition_expression_mock.render().format(),
            ExpressionAttributeNames={"#aaa": "test"},
            ExpressionAttributeValues={":aaa": "data"},
            Key={"pk": "value", "sk": "value"},
            ReturnConsumedCapacity="NONE",
            ReturnItemCollectionMetrics="NONE",
            ReturnValues="ALL_NEW",
            UpdateExpression="SET #aaa = :aaa",
        )
        assert list(result.get_records()) == []

    @staticmethod
    def test_delete_item() -> None:
        condition_expression_mock = MagicMock()
        table_resource_mock = MagicMock()
        query = DynamoQuery.build_delete_item(
            condition_expression=condition_expression_mock,
        ).table(table=table_resource_mock, table_keys=("pk", "sk"))
        result = query.execute_dict({"pk": "value", "sk": "value", "test": "data"})
        table_resource_mock.delete_item.assert_called_with(
            ConditionExpression=condition_expression_mock.render().format(),
            Key={"pk": "value", "sk": "value"},
            ReturnConsumedCapacity="NONE",
            ReturnItemCollectionMetrics="NONE",
            ReturnValues="ALL_OLD",
        )
        assert list(result.get_records()) == []

    @staticmethod
    def test_batch_get_item() -> None:
        table_resource_mock = MagicMock()
        query = DynamoQuery.build_batch_get_item().table(
            table=table_resource_mock, table_keys=("pk", "sk")
        )
        result = query.execute_dict({"pk": "value", "sk": "value"})
        table_resource_mock.meta.client.batch_get_item.assert_called_with(
            RequestItems={
                table_resource_mock.name: {"Keys": [{"pk": "value", "sk": "value"}]}
            },
            ReturnConsumedCapacity="NONE",
        )
        assert list(result.get_records()) == [{"pk": "value", "sk": "value"}]

    @staticmethod
    def test_batch_update_item() -> None:
        table_resource_mock = MagicMock()
        query = DynamoQuery.build_batch_update_item().table(
            table=table_resource_mock, table_keys=("pk", "sk")
        )
        result = query.execute_dict({"pk": "value", "sk": "value"})
        table_resource_mock.meta.client.batch_write_item.assert_called_with(
            RequestItems={
                table_resource_mock.name: [
                    {"PutRequest": {"Item": {"pk": "value", "sk": "value"}}}
                ]
            },
            ReturnConsumedCapacity="NONE",
            ReturnItemCollectionMetrics="NONE",
        )
        assert list(result.get_records()) == [{"pk": "value", "sk": "value"}]

    @staticmethod
    def test_batch_delete_item() -> None:
        table_resource_mock = MagicMock()
        query = DynamoQuery.build_batch_delete_item().table(
            table=table_resource_mock, table_keys=("pk", "sk")
        )
        result = query.execute_dict({"pk": "value", "sk": "value"})
        table_resource_mock.meta.client.batch_write_item.assert_called_with(
            RequestItems={
                table_resource_mock.name: [
                    {"DeleteRequest": {"Key": {"pk": "value", "sk": "value"}}}
                ]
            },
            ReturnConsumedCapacity="NONE",
            ReturnItemCollectionMetrics="NONE",
        )
        assert list(result.get_records()) == [{"pk": "value", "sk": "value"}]
