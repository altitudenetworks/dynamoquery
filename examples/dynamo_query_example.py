"""
Usage examples for `DynamoQuery` class.
"""
from dataclasses import dataclass

from dynamo_query.data_table import DataTable
from dynamo_query.dynamo_query_main import DynamoQuery
from dynamo_query.dynamo_record import DynamoRecord
from dynamo_query.expressions import ConditionExpression


# define keys of a record structure
@dataclass
class UserRecord(DynamoRecord):
    pk: str
    sk: str
    email: str
    company: str
    name: str
    age: int


def main() -> None:
    users_table = DataTable[UserRecord](record_class=UserRecord).add_record(
        {
            "pk": "john_student@gmail.com",
            "sk": "IBM",
            "email": "john_student@gmail.com",
            "company": "IBM",
            "name": "John",
            "age": 34,
        },
        {
            "pk": "mary@gmail.com",
            "sk": "CiscoSystems",
            "email": "mary@gmail.com",
            "company": "CiscoSystems",
            "name": "Mary",
            "age": 34,
        },
    )
    DynamoQuery.build_batch_update_item().execute(users_table)

    print("Get all records:")
    for user_record in DynamoQuery.build_scan().execute_dict({}):
        print(user_record)

    print("Get John's record:")
    print(DynamoQuery.build_get_item().execute_dict({"pk": "john_student@gmail.com", "sk": "IBM",}))

    print("Query by a specific index:")
    print(
        DynamoQuery.build_query(
            index_name="lsi_name", key_condition_expression=ConditionExpression("name")
        )
        .execute_dict({"name": "Mary"})
        .get_records()
    )


if __name__ == "__main__":
    main()
