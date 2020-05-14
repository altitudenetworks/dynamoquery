import datetime
from unittest.mock import MagicMock

import pytest

from dynamo_query.data_table import DataTable
from dynamo_query.dynamo_table import DynamoTable, DynamoTableError
from dynamo_query.expressions import ConditionExpression
from dynamo_query.dynamo_table_index import DynamoTableIndex


@pytest.fixture
def _patch_datetime(monkeypatch):
    class DatetimeMock:
        @classmethod
        def utcnow(cls):
            utcnow_mock = MagicMock()
            utcnow_mock.isoformat.return_value = "utcnow"
            return utcnow_mock

    monkeypatch.setattr(datetime, "datetime", DatetimeMock)


class TestDynamoTableError:
    result: DynamoTableError
    result_data: DynamoTableError

    def setup_method(self):
        self.result = DynamoTableError("Test")
        self.result_data = DynamoTableError("Test", {"key": "value"})

    def test_init(self):
        assert str(self.result) == "Test"
        assert str(self.result_data) == 'Test data={"key": "value"}'


class TestDynamoTable:
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
            local_secondary_indexes = [DynamoTableIndex("lsi", "lsi_pk", "sk")]

            @property
            def table(self):
                return table_mock

            def get_partition_key(self, record):
                return record["pk_column"]

            def get_sort_key(self, record):
                return record["sk_column"]

        self.result = MyDynamoTable()

    def test_init(self):
        assert self.result.table.name == "my_table_name"

    def test_delete_table(self):
        self.result.delete_table()
        self.table_mock.delete.assert_called_once_with()

    def test_create_table(self):
        self.result.create_table()
        self.client_mock.create_table.assert_called_once_with(
            AttributeDefinitions=[
                {"AttributeName": "pk", "AttributeType": "S"},
                {"AttributeName": "sk", "AttributeType": "S"},
                {"AttributeName": "gsi_pk", "AttributeType": "S"},
                {"AttributeName": "gsi_sk", "AttributeType": "S"},
                {"AttributeName": "lsi_pk", "AttributeType": "S"},
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
                    "KeySchema": [
                        {"AttributeName": "lsi_pk", "KeyType": "HASH"},
                        {"AttributeName": "sk", "KeyType": "RANGE"},
                    ],
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
                "my_table_name": [
                    {"pk": "my_pk", "sk": "my_sk", "data": "value1", "preserve": "p1"}
                ]
            }
        }
        self.client_mock.batch_get_item.return_value = {
            "Responses": {
                "my_table_name": [
                    {"pk": "my_pk", "sk": "my_sk", "data": "value1", "preserve": "p1"}
                ]
            }
        }
        data_table = DataTable().add_record(
            {
                "pk": "my_pk",
                "sk": "my_sk",
                "data": "value2",
                "preserve": "p2",
                "preserve2": "p3",
                "gsi_pk": "gsi_pk",
                "gsi_sk": "gsi_sk",
                "lsi_pk": "lsi_pk",
                "dt_created": None,
            }
        )
        assert list(
            self.result.batch_upsert(
                data_table, set_if_not_exists_keys=["preserve", "preserve2"]
            ).get_records()
        ) == [
            {
                "pk": "my_pk",
                "sk": "my_sk",
                "data": "value2",
                "preserve": "p1",
                "preserve2": "p3",
                "gsi_pk": "gsi_pk",
                "gsi_sk": "gsi_sk",
                "lsi_pk": "lsi_pk",
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
                                "data": "value2",
                                "preserve": "p1",
                                "preserve2": "p3",
                                "gsi_pk": "gsi_pk",
                                "gsi_sk": "gsi_sk",
                                "lsi_pk": "lsi_pk",
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

        with pytest.raises(DynamoTableError):
            self.result.batch_upsert(
                DataTable().add_record(
                    {
                        "pk": "my_pk",
                        "sk": "my_sk",
                        "data": "value2",
                        "preserve": "p2",
                        "preserve2": "p3",
                        "gsi_pk": "gsi_pk",
                        "gsi_sk": "gsi_sk",
                    }
                )
            )
        with pytest.raises(DynamoTableError):
            self.result.batch_upsert(
                DataTable().add_record(
                    {
                        "pk": "my_pk",
                        "sk": "my_sk",
                        "data": "value2",
                        "preserve": "p2",
                        "preserve2": "p3",
                        "gsi_pk": "gsi_pk",
                        "gsi_sk": "gsi_sk",
                        "lsi_pk": 12,
                    }
                )
            )

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
                sort_key="sk_value",
                filter_expression=filter_expression_mock,
                data={"key": ["key_value"]},
                limit=1,
            )
        ) == [{"pk": "my_pk", "sk": "sk"}]
        self.table_mock.query.assert_called_with(
            KeyConditionExpression="#aab = :aaa AND #aac = :aab",
            FilterExpression="#aaa = :aac___0",
            ConsistentRead=False,
            ScanIndexForward=True,
            ExpressionAttributeNames={"#aaa": "key", "#aab": "pk", "#aac": "sk"},
            ExpressionAttributeValues={
                ":aaa": "pk_value",
                ":aab": "sk_value",
                ":aac___0": "key_value",
            },
            Limit=1,
        )
        self.table_mock.reset_mock()
        list(
            self.result.query(partition_key="pk", sort_key_prefix="sk_prefix", limit=1,)
        )
        self.table_mock.query.assert_called_with(
            KeyConditionExpression="#aaa = :aaa AND begins_with(#aab, :aab)",
            ConsistentRead=False,
            ScanIndexForward=True,
            ExpressionAttributeNames={"#aaa": "pk", "#aab": "sk"},
            ExpressionAttributeValues={":aaa": "pk", ":aab": "sk_prefix"},
            Limit=1,
        )

        with pytest.raises(DynamoTableError):
            list(self.result.query(partition_key=None, limit=1))

    def test_wait_until_exists(self):
        self.result.wait_until_exists()
        self.table_mock.wait_until_exists.assert_called_with()

    def test_wait_until_not_exists(self):
        self.result.wait_until_not_exists()
        self.table_mock.wait_until_not_exists.assert_called_with()

    def test_batch_get_records(self):
        self.client_mock.batch_get_item.return_value = {
            "Responses": {
                "my_table_name": [{"pk": "my_pk", "sk": "my_sk", "data": "value"}]
            }
        }
        assert list(
            self.result.batch_get_records([{"pk": "my_pk", "sk": "my_sk"}])
        ) == [{"pk": "my_pk", "sk": "my_sk", "data": "value"}]
        self.client_mock.batch_get_item.assert_called_with(
            RequestItems={"my_table_name": {"Keys": [{"pk": "my_pk", "sk": "my_sk"}]}},
            ReturnConsumedCapacity="NONE",
        )

        assert list(self.result.batch_get(DataTable()).get_records()) == []

    def test_batch_upsert_records(self, _patch_datetime):
        self.client_mock.batch_write_item.return_value = {
            "Responses": {
                "my_table_name": [
                    {"pk": "my_pk", "sk": "my_sk", "data": "value1", "preserve": "p1"}
                ]
            }
        }
        self.client_mock.batch_get_item.return_value = {
            "Responses": {
                "my_table_name": [
                    {"pk": "my_pk", "sk": "my_sk", "data": "value1", "preserve": "p1"}
                ]
            }
        }
        assert list(
            self.result.batch_upsert_records(
                [
                    {
                        "pk": "my_pk",
                        "sk": "my_sk",
                        "data": "value2",
                        "preserve": "p2",
                        "preserve2": "p3",
                        "gsi_pk": "gsi_pk",
                        "gsi_sk": "gsi_sk",
                        "lsi_pk": "lsi_pk",
                        "dt_created": None,
                    }
                ],
                set_if_not_exists_keys=["preserve", "preserve2"],
            )
        ) == [
            {
                "pk": "my_pk",
                "sk": "my_sk",
                "data": "value2",
                "preserve": "p1",
                "preserve2": "p3",
                "gsi_pk": "gsi_pk",
                "gsi_sk": "gsi_sk",
                "lsi_pk": "lsi_pk",
                "dt_created": "utcnow",
                "dt_modified": "utcnow",
            }
        ]

    def test_batch_delete_records(self):
        self.client_mock.batch_write_item.return_value = {
            "Responses": {
                "my_table_name": [{"pk": "my_pk", "sk": "my_sk", "data": "value"}]
            }
        }
        records = (i for i in [{"pk": "my_pk", "sk": "my_sk"}])
        assert list(self.result.batch_delete_records(records)) == [
            {"pk": "my_pk", "sk": "my_sk"}
        ]
