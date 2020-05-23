"""
Usage examples for `DynamoTable` class.
"""
from dataclasses import dataclass
from typing import Optional

import boto3
from mypy_boto3.dynamodb.service_resource import DynamoDBServiceResource, Table

from dynamo_query.data_table import DataTable
from dynamo_query.dynamo_record import DynamoRecord
from dynamo_query.dynamo_table import DynamoTable
from dynamo_query.dynamo_table_index import DynamoTableIndex


@dataclass
class UserRecord(DynamoRecord):
    # define required keys of a record structure
    email: str
    company: str

    # define optional keys of a record structure
    pk: Optional[str] = None
    sk: Optional[str] = None
    name: Optional[str] = None
    age: Optional[int] = None


class UserDynamoTable(DynamoTable):
    gsi_name_age = DynamoTableIndex("gsi_name_age", "name", "age", sort_key_type="N")
    lsi_name = DynamoTableIndex("lsi_name", "name", None)
    global_secondary_indexes = [gsi_name_age]
    local_secondary_indexes = [lsi_name]

    @property
    def table(self) -> Table:
        resource: DynamoDBServiceResource = boto3.resource("dynamodb")
        return resource.Table("users_table")  # pylint: disable=no-member

    def get_partition_key(self, record: UserRecord) -> str:
        return record.email

    def get_sort_key(self, record: UserRecord) -> str:
        return record.company


def main() -> None:
    user_dynamo_table = UserDynamoTable()
    users_table = DataTable[UserRecord]().add_record(
        UserRecord(email="john_student@gmail.com", company="IBM", name="John", age=34),
        UserRecord.fromdict(
            dict(email="mary@gmail.com", company="CiscoSystems", name="Mary", age=34)
        ),
    )
    user_dynamo_table.batch_upsert(users_table)

    print("Get all records:")
    for user_record in user_dynamo_table.scan():
        print(user_record)

    print("Get John's record:")
    print(user_dynamo_table.get_record({"email": "john_student@gmail.com", "company": "IBM"}))

    print("Query by a specific index:")
    print(list(user_dynamo_table.query(index=UserDynamoTable.lsi_name, partition_key="Mary")))


if __name__ == "__main__":
    main()
