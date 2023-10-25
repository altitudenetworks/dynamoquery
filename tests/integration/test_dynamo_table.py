from typing import Dict, Optional

import boto3
import pytest

from botocore import exceptions

from dynamo_query.data_table import DataTable
from dynamo_query.dictclasses.dynamo_dictclass import DynamoDictClass
from dynamo_query.dynamo_table import DynamoTable
from dynamo_query.dynamo_table_index import DynamoTableIndex
from dynamo_query.expressions import ConditionExpression


class UserRecord(DynamoDictClass):
    project_id: str = "my_project"
    company: str
    email: str
    name: Optional[str] = None
    age: Optional[int] = None
    dt_created: Optional[str] = None
    dt_modified: Optional[str] = None
    nested: Optional[Dict] = None

    @DynamoDictClass.compute_key("pk")
    def get_pk(self) -> str:
        return self.project_id

    @DynamoDictClass.compute_key("sk")
    def get_sk(self) -> str:
        return self.company


class UserDynamoTable(DynamoTable[UserRecord]):
    gsi_name_age = DynamoTableIndex("gsi_name_age", "name", "age", sort_key_type="N")
    global_secondary_indexes = [gsi_name_age]
    record_class = UserRecord

    read_capacity_units = 50
    write_capacity_units = 10

    @property
    def table(self):
        resource: DynamoDBServiceResource = boto3.resource(
            "dynamodb",
            endpoint_url="http://localhost:8000",
            region_name="us-west-1",
            aws_access_key_id="null",
            aws_secret_access_key="null",
        )
        return resource.Table("test_dq_users_table")  # pylint: disable=no-member


@pytest.mark.integration
class TestDataTable:
    @classmethod
    def setup_class(cls):
        cls.table = UserDynamoTable()
        cls.table.create_table()
        cls.table.wait_until_exists()

    def setup_method(self):
        self.table.clear_table()

    def test_create_pay_per_request(self):
        class Cheap(DynamoTable):
            "Use default 'pk' and 'sk' for keys."
            @property
            def table(self):
                resource: DynamoDBServiceResource = boto3.resource(
                    "dynamodb",
                    endpoint_url="http://localhost:8000",
                    region_name="us-west-1",
                    aws_access_key_id="null",
                    aws_secret_access_key="null",
                )
                return resource.Table("test_dq_cheap_table")  # pylint: disable=no-member

        table = Cheap()
        table.create_table()

    def test_clear_table(self):
        self.table.upsert_record(
            UserRecord(email="john_student@gmail.com", company="IBM", name="John", age=34)
        )
        assert len(list(self.table.scan())) == 1
        self.table.clear_table()
        assert list(self.table.scan()) == []

    def test_batch_upsert(self):
        users_table = DataTable[UserRecord](record_class=UserRecord).add_record(
            UserRecord(email="john_student@gmail.com", company="IBM", name="John", age=34),
            dict(email="mary@gmail.com", company="CiscoSystems", name="Mary", age=34),
        )
        self.table.batch_upsert(users_table)
        assert len(list(self.table.scan())) == 2
        records = list(self.table.scan())
        emails = set([i.email for i in records])
        assert emails == {"john_student@gmail.com", "mary@gmail.com"}

    def test_get_record(self):
        self.table.upsert_record(
            UserRecord(email="john_student@gmail.com", company="IBM", name="John", age=34)
        )
        record = self.table.get_record(UserRecord(email="john_student@gmail.com", company="IBM"))
        assert record.age == 34
        record = self.table.get_record(UserRecord(email="john_student@gmail.com", company="IBM1"))
        assert record is None

    def test_batch_get_records(self):
        record = UserRecord(email="john_student@gmail.com", company="IBM", name="John", age=34)
        self.table.upsert_record(record)
        for record in self.table.batch_get_records((i for i in [record])):
            assert record.age == 34

    def test_batch_upsert_records(self):
        record = UserRecord(email="john_student@gmail.com", company="IBM", name="John", age=34)
        self.table.batch_upsert_records([record])
        for record in self.table.batch_get_records((i for i in [record])):
            assert record.age == 34

    def test_batch_delete_records(self):
        record = UserRecord(email="john_student@gmail.com", company="IBM", name="John", age=34)
        self.table.upsert_record(record)
        assert len(list(self.table.scan())) == 1
        self.table.batch_delete_records([UserRecord(email="john_student@gmail.com", company="IBM")])
        assert len(list(self.table.scan())) == 0

    def test_query(self):
        record = UserRecord(
            email="john_student@gmail.com",
            company="IBM",
            name="John",
            age=34,
            nested={"test": {"deep": "value"}},
        )
        self.table.upsert_record(record)
        assert (
            len(
                list(
                    self.table.query(
                        partition_key="my_project",
                        filter_expression=ConditionExpression("nested.test.deep"),
                        data={"nested.test.deep": "value"},
                    )
                )
            )
            == 1
        )
        assert (
            len(
                list(
                    self.table.query(
                        partition_key="my_project",
                        filter_expression=ConditionExpression("nested.test.deep"),
                        data={"nested.test.deep": "none"},
                    )
                )
            )
            == 0
        )

    def test_upsert_record_condition_accept(self):
        record = UserRecord(
            email="john_student@gmail.com",
            company="IBM",
            name="John",
            age=34,
        )
        self.table.upsert_record(
            record,
            ConditionExpression("email", "attribute_not_exists"),
        )
        assert len(list(self.table.scan())) == 1

    def test_upsert_record_condition_reject(self):
        record = UserRecord(
            email="john_student@gmail.com",
            company="IBM",
            name="John",
            age=34,
        )
        with pytest.raises(exceptions.ClientError) as err:
            self.table.upsert_record(
                record,
                ConditionExpression("email", "attribute_exists"),
            )
        assert err.value.response["Error"]["Code"] == "ConditionalCheckFailedException"
        assert len(list(self.table.scan())) == 0

    def test_upsert_record_condition_reject_2(self):
        record = UserRecord(
            email="john_student@gmail.com",
            company="IBM",
            name="John",
            age=34,
        )
        self.table.upsert_record(record)

        new_record = UserRecord(
            email="john_student@gmail.com",
            company="IBM",
            name="Johnny",
            age=48,
        )
        with pytest.raises(exceptions.ClientError) as err:
            self.table.upsert_record(
                new_record,
                ConditionExpression("age", "<", "check_age"),
                extra_data={"check_age": 30}
            )
        assert err.value.response["Error"]["Code"] == "ConditionalCheckFailedException"

        for record in self.table.batch_get_records((i for i in [record])):
            assert record.name == "John"
            assert record.age == 34
