from unittest.mock import MagicMock

from dynamo_query.dynamo_table import DynamoTable
from dynamo_query.dynamo_table_index import DynamoTableIndex


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

    # def test_clear_table(self):
    #     self.result.clear_table("pk_value")
