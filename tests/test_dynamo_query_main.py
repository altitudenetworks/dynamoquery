from unittest.mock import ANY, MagicMock

import pytest

from dynamo_query.data_table import DataTable
from dynamo_query.dynamo_query_main import DynamoQuery, DynamoQueryError
from dynamo_query.expressions import ConditionExpression, ProjectionExpression, UpdateExpression


class TestDynamoQuery:
    table_resource_mock: MagicMock

    def setup_method(self):
        self.table_name = "table_name"
        self.table_resource_mock = MagicMock()
        self.table_resource_mock.name = self.table_name

    def test_methods(self):
        table_resource_mock = MagicMock()
        query = DynamoQuery.build_query(
            key_condition_expression=ConditionExpression("key"),
            index_name="my_index",
            filter_expression=ConditionExpression("test"),
            limit=100,
        ).projection("return")

        with pytest.raises(DynamoQueryError):
            _ = query.table_resource

        with pytest.raises(DynamoQueryError):
            _ = query.table_keys

        query.table(table=table_resource_mock)
        assert str(query) == "<DynamoQuery type=query>"
        assert query.table_resource == table_resource_mock
        assert not query.was_executed()
        assert query.has_more_results()

        query.execute_dict({"key": "value", "test": "data"})
        assert query.was_executed()
        assert query.has_more_results()
        assert query.get_last_evaluated_key() == table_resource_mock.query().get()
        assert query.get_raw_responses() == [table_resource_mock.query()]

        table_resource_mock.key_schema = [
            {"AttributeName": "key"},
            {"NotKey": "not_key"},
        ]
        assert query.get_table_keys(table_resource_mock) == {"key"}
        assert query.limit(10)

        with pytest.raises(DynamoQueryError):
            DynamoQuery.build_batch_get_item().limit(10)

    def test_expression_methods(self):
        query = DynamoQuery.build_batch_get_item()

        with pytest.raises(DynamoQueryError):
            query.update("key")

        with pytest.raises(DynamoQueryError):
            query.projection("key")

    def test_errors(self):
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
            query.execute(DataTable({"key": [1, 2], "b": [3]}))

        with pytest.raises(DynamoQueryError):
            query.execute(DataTable({"key": [3, DataTable.NOT_SET]}))

    def test_query(self):
        table_resource_mock = MagicMock()
        query = (
            DynamoQuery.build_query(
                key_condition_expression=ConditionExpression("pk"),
                index_name="my_index",
                filter_expression=ConditionExpression("test"),
                projection_expression=ProjectionExpression("test2"),
                exclusive_start_key={"pk": "my_pk", "sk": "my_sk"},
                limit=100,
            )
            .table(table=table_resource_mock, table_keys=("pk", "sk"))
            .projection("test")
        )
        result = query.execute_dict({"pk": "pk_value", "test": "data"})
        table_resource_mock.query.assert_called_with(
            ConsistentRead=False,
            ExclusiveStartKey={"pk": "my_pk", "sk": "my_sk"},
            ExpressionAttributeNames={"#aaa": "pk", "#aab": "test"},
            ExpressionAttributeValues={":aaa": "pk_value", ":aab": "data"},
            FilterExpression="#aab = :aab",
            IndexName="my_index",
            KeyConditionExpression="#aaa = :aaa",
            Limit=100,
            ProjectionExpression="#aab",
            ScanIndexForward=True,
        )
        assert list(result.get_records()) == []
        query.reset_start_key().execute(
            DataTable().add_record(
                {"pk": "pk_value", "test": "data"}, {"pk": "pk_value2", "test": "data"}
            )
        )
        table_resource_mock.query.assert_called_with(
            ConsistentRead=False,
            ExclusiveStartKey=ANY,
            ExpressionAttributeNames={"#aaa": "pk", "#aab": "test"},
            ExpressionAttributeValues={":aaa": "pk_value2", ":aab": "data"},
            FilterExpression="#aab = :aab",
            IndexName="my_index",
            KeyConditionExpression="#aaa = :aaa",
            Limit=100,
            ProjectionExpression="#aab",
            ScanIndexForward=True,
        )

        with pytest.raises(DynamoQueryError):
            query = (
                DynamoQuery.build_query(
                    key_condition_expression=ConditionExpression("pk"),
                    index_name="my_index",
                    exclusive_start_key={"pk": "my_pk"},
                    limit=100,
                )
                .table(table=table_resource_mock, table_keys=("pk", "sk"))
                .projection("test")
                .execute_dict({})
            )

    def test_scan(self):
        table_resource_mock = MagicMock()
        query = (
            DynamoQuery.build_scan(
                filter_expression=ConditionExpression("test"),
                projection_expression=ProjectionExpression("test2"),
                limit=100,
            )
            .table(table=table_resource_mock, table_keys=("pk", "sk"))
            .projection("test")
        )
        result = query.execute_dict({"test": "value"})
        table_resource_mock.scan.assert_called_with(
            ExpressionAttributeNames={"#aaa": "test"},
            ExpressionAttributeValues={":aaa": "value"},
            FilterExpression="#aaa = :aaa",
            Limit=100,
            ProjectionExpression="#aaa",
        )
        assert list(result.get_records()) == []

    def test_get_item(self):
        table_resource_mock = MagicMock()
        query = (
            DynamoQuery.build_get_item(projection_expression=ProjectionExpression("test2"),)
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

    def test_update_item(self):
        table_resource_mock = MagicMock()
        query = (
            DynamoQuery.build_update_item(
                update_expression=UpdateExpression("test2"),
                condition_expression=ConditionExpression("pk"),
            )
            .table(table=table_resource_mock, table_keys=("pk", "sk"))
            .update("test")
        )
        result = query.execute_dict({"pk": "pk_value", "sk": "sk_value", "test": "data"})
        table_resource_mock.update_item.assert_called_with(
            ConditionExpression="#aaa = :aaa",
            ExpressionAttributeNames={"#aaa": "pk", "#aab": "test"},
            ExpressionAttributeValues={":aaa": "pk_value", ":aab": "data"},
            Key={"pk": "pk_value", "sk": "sk_value"},
            ReturnConsumedCapacity="NONE",
            ReturnItemCollectionMetrics="NONE",
            ReturnValues="ALL_NEW",
            UpdateExpression="SET #aab = :aab",
        )
        assert list(result.get_records()) == []

        with pytest.raises(DynamoQueryError):
            DynamoQuery.build_update_item(condition_expression=ConditionExpression("pk"),).table(
                table=table_resource_mock, table_keys=("pk", "sk")
            ).execute_dict({"pk": "value", "sk": "value", "test": "data"})

        with pytest.raises(DynamoQueryError):
            DynamoQuery.build_update_item(condition_expression=ConditionExpression("pk"),).table(
                table=table_resource_mock, table_keys=("pk", "sk")
            ).update(add=["test"],).execute_dict({"pk": "value", "sk": "value", "test": "data"})

    def test_delete_item(self):
        table_resource_mock = MagicMock()
        query = DynamoQuery.build_delete_item(
            condition_expression=ConditionExpression("test"),
        ).table(table=table_resource_mock, table_keys=("pk", "sk"))
        result = query.execute_dict({"pk": "pk_value", "sk": "sk_value", "test": "data"})
        table_resource_mock.delete_item.assert_called_with(
            ConditionExpression="#aaa = :aaa",
            ExpressionAttributeNames={"#aaa": "test"},
            ExpressionAttributeValues={":aaa": "data"},
            Key={"pk": "pk_value", "sk": "sk_value"},
            ReturnConsumedCapacity="NONE",
            ReturnItemCollectionMetrics="NONE",
            ReturnValues="ALL_OLD",
        )
        assert list(result.get_records()) == []

    def test_batch_get_item(self):
        query = DynamoQuery.build_batch_get_item().table(
            table=self.table_resource_mock, table_keys=("pk", "sk")
        )
        self.table_resource_mock.meta.client.batch_get_item.return_value = {
            "Responses": {
                "table_name": [
                    {"pk": "value", "sk": "value", "other": "test"},
                    {"pk": "value", "sk": "value2", "other": "test2"},
                ]
            }
        }
        result = query.execute_dict({"pk": "value", "sk": "value"})
        self.table_resource_mock.meta.client.batch_get_item.assert_called_with(
            RequestItems={"table_name": {"Keys": [{"pk": "value", "sk": "value"}]}},
            ReturnConsumedCapacity="NONE",
        )
        assert list(result.get_records()) == [{"pk": "value", "sk": "value", "other": "test"}]

    def test_batch_update_item(self):
        query = DynamoQuery.build_batch_update_item().table(
            table=self.table_resource_mock, table_keys=("pk", "sk")
        )
        result = query.execute_dict({"pk": "value", "sk": "value", "new_key": "new_value"})
        self.table_resource_mock.meta.client.batch_write_item.assert_called_with(
            RequestItems={
                "table_name": [
                    {"PutRequest": {"Item": {"pk": "value", "sk": "value", "new_key": "new_value"}}}
                ]
            },
            ReturnConsumedCapacity="NONE",
            ReturnItemCollectionMetrics="NONE",
        )
        assert list(result.get_records()) == [
            {"pk": "value", "sk": "value", "new_key": "new_value"}
        ]

    def test_batch_delete_item(self):
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
