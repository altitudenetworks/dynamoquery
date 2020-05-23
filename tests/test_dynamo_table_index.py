from dynamo_query.dynamo_table_index import DynamoTableIndex


class TestDynamoTableIndex:
    result: DynamoTableIndex
    no_sort_key_index: DynamoTableIndex
    primary: DynamoTableIndex

    def setup_method(self):
        self.result = DynamoTableIndex("my_index", "pk", "sk")
        self.no_sort_key_index = DynamoTableIndex("no_sort_key_index", "pk", "")
        self.primary = DynamoTableIndex(DynamoTableIndex.PRIMARY, "pk", "sk")

    def test_init(self) -> None:
        assert self.result.name == "my_index"
        assert self.result.partition_key_name == "pk"
        assert self.result.sort_key_name == "sk"
        assert self.primary.name is None
        assert str(self.result) == "<DynamoTableIndex name=my_index>"

    def test_as_global_secondary_index(self) -> None:
        assert self.result.as_global_secondary_index() == {
            "IndexName": "my_index",
            "KeySchema": [
                {"AttributeName": "pk", "KeyType": "HASH"},
                {"AttributeName": "sk", "KeyType": "RANGE"},
            ],
            "Projection": {"ProjectionType": "ALL"},
        }
        assert self.no_sort_key_index.as_global_secondary_index() == {
            "IndexName": "no_sort_key_index",
            "KeySchema": [{"AttributeName": "pk", "KeyType": "HASH"}],
            "Projection": {"ProjectionType": "ALL"},
        }

    def test_as_local_secondary_index(self) -> None:
        assert self.result.as_local_secondary_index() == {
            "IndexName": "my_index",
            "KeySchema": [
                {"AttributeName": "pk", "KeyType": "HASH"},
                {"AttributeName": "sk", "KeyType": "RANGE"},
            ],
            "Projection": {"ProjectionType": "ALL"},
        }
        assert self.no_sort_key_index.as_local_secondary_index() == {
            "IndexName": "no_sort_key_index",
            "KeySchema": [{"AttributeName": "pk", "KeyType": "HASH"}],
            "Projection": {"ProjectionType": "ALL"},
        }

    def test_as_key_schema(self) -> None:
        assert self.result.as_key_schema() == [
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ]
        assert self.no_sort_key_index.as_key_schema() == [
            {"AttributeName": "pk", "KeyType": "HASH"},
        ]

    def test_as_attribute_definitions(self) -> None:
        assert self.result.as_attribute_definitions() == [
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
        ]
        assert self.no_sort_key_index.as_attribute_definitions() == [
            {"AttributeName": "pk", "AttributeType": "S"},
        ]

    def test_get_query_data(self) -> None:
        assert self.result.get_query_data("pk_value", "sk_value") == {
            "pk": "pk_value",
            "sk": "sk_value",
        }
        assert self.result.get_query_data("pk_value", None) == {"pk": "pk_value"}
