"""
Usage examples for `DynamoQuery` class.
"""
from typing_extensions import TypedDict, Literal

from dynamo_query.data_table import DataTable
from dynamo_query.dynamo_query import DynamoQuery
from dynamo_query.expressions import ConditionExpression


# define keys of a record structure
class UserRecord(TypedDict):
    pk: str
    sk: str
    email: str
    company: Literal["IBM", "CiscoSystems"]
    name: str
    age: int


def main() -> None:
    users_table = DataTable[UserRecord]().add_record(
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
    print(
        DynamoQuery.build_get_item().execute_dict(
            {"pk": "john_student@gmail.com", "sk": "IBM",}
        )
    )

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
