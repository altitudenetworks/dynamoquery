"""
Usage examples for `DynamoTable` class.
"""
from typing import Optional

import boto3
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table

from dynamo_query.dictclasses.dynamo_dictclass import DynamoDictClass
from dynamo_query.dynamo_table import DynamoTable
from dynamo_query.dynamo_table_index import DynamoTableIndex


class UserRecord(DynamoDictClass):
    pk: str
    project_id: str
    company: str
    email: str
    name: Optional[str] = None
    age: Optional[int] = None
    dt_created: Optional[str] = None
    dt_modified: Optional[str] = None

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
    def table(self) -> Table:
        resource: DynamoDBServiceResource = boto3.resource("dynamodb")
        return resource.Table("test_dq_users_table")  # pylint: disable=no-member


def main() -> None:
    user_dynamo_table = UserDynamoTable()
    user_dynamo_table.create_table()
    user_dynamo_table.wait_until_exists()
    user_dynamo_table.clear_table()

    user_dynamo_table.batch_upsert_records(
        [
            UserRecord(
                project_id="my_project",
                email="john_student@gmail.com",
                company="IBM",
                name="John",
                age=34,
            ),
            UserRecord(
                project_id="my_project",
                email="mary@gmail.com",
                company="CiscoSystems",
                name="Mary",
                age=34,
            ),
        ]
    )

    print("Get all records:")
    for user_record in user_dynamo_table.scan():
        print(user_record)

    print("Get John's record:")
    print(
        user_dynamo_table.get_record(
            UserRecord({"email": "john_student@gmail.com", "company": "IBM"})
        )
    )

    print("Query by a specific index:")
    print(
        list(
            user_dynamo_table.query(
                index=UserDynamoTable.gsi_name_age, partition_key="Mary", sort_key=34
            )
        )
    )

    print("Using iterators for batch methods:")
    record = UserRecord({"email": "john_student@gmail.com", "company": "IBM"})
    for full_record in user_dynamo_table.batch_get_records((i for i in [record])):
        print(full_record)

    user_dynamo_table.batch_upsert_records([record])
    user_dynamo_table.batch_delete_records((i for i in [record]))


if __name__ == "__main__":
    main()
