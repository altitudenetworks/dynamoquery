import datetime
from unittest.mock import MagicMock

import pytest

from dynamo_query.data_table import DataTable
from dynamo_query.dynamo_table import DynamoTable
from dynamo_query.expressions import ConditionExpression
from dynamo_query.dynamo_table_index import DynamoTableIndex


@pytest.fixture
def _patch_datetime(monkeypatch):
    class DatetimeMock:
        @classmethod
        def utcnow(cls):
            return "utcnow"

    monkeypatch.setattr(datetime, "datetime", DatetimeMock)


class TestDynamoTableIndex:
    result: DynamoTable
    primary: DynamoTable
    table_mock: MagicMock
    client_mock: MagicMock

    def setup_method(self):
        client_mock = MagicMock()
        self.client_mock = client_mock

        table_mock = MagicMock()
        table_mock.name = "my_table_name"
        table_mock.meta.client = client_mock
        self.table_mock = table_mock

        class MyDynamoTable(DynamoTable):
            global_secondary_indexes = [DynamoTableIndex("gsi", "gsi_pk", "gsi_sk")]
            local_secondary_indexes = [DynamoTableIndex("lsi", "lsi_pk", None)]

            @property
            def table(self):
                return table_mock

            def _get_partition_key(self, record):
                return record["pk_column"]

            def _get_sort_key(self, record):
                return record["sk_column"]

        self.result = MyDynamoTable()

    def test_init(self):
        assert self.result.table.name == "my_table_name"

    def test_get_partition_key(self):
        assert self.result.get_partition_key({"pk_column": "my_pk"}) == "my_pk"
        assert (
            self.result.get_partition_key({"pk": "my_pk", "pk_column": "not_pk"})
            == "my_pk"
        )

    def test_get_sort_key(self):
        assert self.result.get_sort_key({"sk_column": "my_sk"}) == "my_sk"
        assert (
            self.result.get_sort_key({"sk": "my_sk", "sk_column": "not_sk"}) == "my_sk"
        )

    def test_create_table(self):
        self.result.create_table()
        self.client_mock.create_table.assert_called_once_with(
            AttributeDefinitions=[
                {"AttributeName": "pk", "AttributeType": "S"},
                {"AttributeName": "sk", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "gsi",
                    "KeySchema": [
                        {"AttributeName": "gsi_pk", "KeyType": "HASH"},
                        {"AttributeName": "gsi_sk", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            KeySchema=[
                {"AttributeName": "pk", "KeyType": "HASH"},
                {"AttributeName": "sk", "KeyType": "RANGE"},
            ],
            LocalSecondaryIndexes=[
                {
                    "IndexName": "lsi",
                    "KeySchema": [{"AttributeName": "lsi_pk", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            TableName="my_table_name",
        )

    def test_clear_table(self):
        self.table_mock.query.return_value = {"Items": [{"pk": "my_pk", "sk": "sk"}]}
        self.table_mock.scan.return_value = {"Items": [{"pk": "my_pk", "sk": "sk"}]}
        self.result.clear_table("my_pk")
        self.table_mock.query.assert_called_with(
            ConsistentRead=False,
            ExpressionAttributeNames={"#aaa": "pk", "#aab": "sk"},
            ExpressionAttributeValues={":aaa": "my_pk"},
            KeyConditionExpression="#aaa = :aaa",
            Limit=1000,
            ProjectionExpression="#aaa, #aab",
            ScanIndexForward=True,
        )
        self.client_mock.batch_write_item.assert_called_with(
            RequestItems={
                "my_table_name": [
                    {"DeleteRequest": {"Key": {"pk": "my_pk", "sk": "sk"}}}
                ]
            },
            ReturnConsumedCapacity="NONE",
            ReturnItemCollectionMetrics="NONE",
        )

        self.result.clear_table(None)
        self.table_mock.scan.assert_called_with(
            ExpressionAttributeNames={"#aaa": "pk", "#aab": "sk"},
            Limit=1000,
            ProjectionExpression="#aaa, #aab",
        )
        self.client_mock.batch_write_item.assert_called_with(
            RequestItems={
                "my_table_name": [
                    {"DeleteRequest": {"Key": {"pk": "my_pk", "sk": "sk"}}}
                ]
            },
            ReturnConsumedCapacity="NONE",
            ReturnItemCollectionMetrics="NONE",
        )

        self.table_mock.scan.return_value = {"Items": []}
        self.result.clear_table(None)

    def test_batch_get(self):
        self.client_mock.batch_get_item.return_value = {
            "Responses": {
                "my_table_name": [{"pk": "my_pk", "sk": "my_sk", "data": "value"}]
            }
        }
        data_table = DataTable().add_record({"pk": "my_pk", "sk": "my_sk"})
        assert list(self.result.batch_get(data_table).get_records()) == [
            {"pk": "my_pk", "sk": "my_sk", "data": "value"}
        ]
        self.client_mock.batch_get_item.assert_called_with(
            RequestItems={"my_table_name": {"Keys": [{"pk": "my_pk", "sk": "my_sk"}]}},
            ReturnConsumedCapacity="NONE",
        )

        assert list(self.result.batch_get(DataTable()).get_records()) == []

    def test_batch_delete(self):
        self.client_mock.batch_write_item.return_value = {
            "Responses": {
                "my_table_name": [{"pk": "my_pk", "sk": "my_sk", "data": "value"}]
            }
        }
        data_table = DataTable().add_record({"pk": "my_pk", "sk": "my_sk"})
        assert list(self.result.batch_delete(data_table).get_records()) == [
            {"pk": "my_pk", "sk": "my_sk"}
        ]
        self.client_mock.batch_write_item.assert_called_with(
            RequestItems={
                "my_table_name": [
                    {"DeleteRequest": {"Key": {"pk": "my_pk", "sk": "my_sk"}}}
                ]
            },
            ReturnConsumedCapacity="NONE",
            ReturnItemCollectionMetrics="NONE",
        )

        assert list(self.result.batch_delete(DataTable()).get_records()) == []

    def test_batch_upsert(self, _patch_datetime):
        self.client_mock.batch_write_item.return_value = {
            "Responses": {
                "my_table_name": [{"pk": "my_pk", "sk": "my_sk", "data": "value1"}]
            }
        }
        data_table = DataTable().add_record(
            {"pk": "my_pk", "sk": "my_sk", "data": "value1"}
        )
        assert list(self.result.batch_upsert(data_table).get_records()) == [
            {
                "pk": "my_pk",
                "sk": "my_sk",
                "data": "value1",
                "dt_created": "utcnow",
                "dt_modified": "utcnow",
            }
        ]
        self.client_mock.batch_write_item.assert_called_with(
            RequestItems={
                "my_table_name": [
                    {
                        "PutRequest": {
                            "Item": {
                                "pk": "my_pk",
                                "sk": "my_sk",
                                "data": "value1",
                                "dt_created": "utcnow",
                                "dt_modified": "utcnow",
                            }
                        }
                    }
                ]
            },
            ReturnConsumedCapacity="NONE",
            ReturnItemCollectionMetrics="NONE",
        )

        assert list(self.result.batch_upsert(DataTable()).get_records()) == []

    def test_get_record(self):
        self.table_mock.get_item.return_value = {
            "Item": {"pk": "my_pk", "pk_column": "my_pk"}
        }
        assert self.result.get_record({"pk_column": "my_pk", "sk_column": "my_sk"}) == {
            "pk": "my_pk",
            "pk_column": "my_pk",
            "sk": "my_sk",
        }
        self.table_mock.get_item.return_value = {"Item": {"pk": "my_pk"}}
        assert (
            self.result.get_record({"pk_column": "my_pk", "sk_column": "my_sk"}) is None
        )

    def test_upsert_record(self):
        self.table_mock.update_item.return_value = {
            "Attributes": {"pk": "my_pk", "pk_column": "my_pk"}
        }
        assert self.result.upsert_record(
            {"pk_column": "my_pk", "sk_column": "my_sk"}
        ) == {"pk": "my_pk", "pk_column": "my_pk"}

    def test_delete_record(self):
        self.table_mock.delete_item.return_value = {
            "Attributes": {"pk": "my_pk", "pk_column": "my_pk"}
        }
        assert self.result.delete_record(
            {"pk_column": "my_pk", "sk_column": "my_sk"}
        ) == {"pk": "my_pk", "pk_column": "my_pk"}
        self.table_mock.delete_item.return_value = {}
        assert (
            self.result.delete_record({"pk_column": "my_pk", "sk_column": "my_sk"})
            is None
        )

    def test_scan(self):
        self.table_mock.scan.return_value = {
            "Items": [{"pk": "my_pk", "sk": "sk"}, {"pk": "my_pk2", "sk": "sk2"}]
        }
        filter_expression_mock = MagicMock()
        assert list(
            self.result.scan(
                filter_expression=filter_expression_mock,
                data={"key": "value"},
                limit=1,
            )
        ) == [{"pk": "my_pk", "sk": "sk"}]
        self.table_mock.scan.assert_called_with(
            FilterExpression=filter_expression_mock.render().format(), Limit=1
        )

    def test_query(self):
        self.table_mock.query.return_value = {
            "Items": [{"pk": "my_pk", "sk": "sk"}, {"pk": "my_pk2", "sk": "sk2"}]
        }
        filter_expression_mock = ConditionExpression("key")
        assert list(
            self.result.query(
                partition_key="pk_value",
                sort_key_prefix="sk_prefix",
                filter_expression=filter_expression_mock,
                data={"key": ["value"]},
                limit=1,
            )
        ) == [{"pk": "my_pk", "sk": "sk"}]
        self.table_mock.query.assert_called_with(
            ConsistentRead=False,
            ExpressionAttributeNames={"#aaa": "key", "#aab": "pk", "#aac": "sk"},
            ExpressionAttributeValues={
                ":aaa": "pk_value",
                ":aab": "sk_prefix",
                ":aac___0": "value",
            },
            FilterExpression="#aaa = :aac___0",
            KeyConditionExpression="#aab = :aaa AND begins_with(#aac, :aab)",
            Limit=1,
            ScanIndexForward=True,
        )

