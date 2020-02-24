"""
Usage examples for `DataTable` class.
"""
from typing_extensions import TypedDict, Literal

from dynamo_query.data_table import DataTable


# define required keys of a record structure
class UserRecordKeys(TypedDict):
    email: str
    company: Literal["IBM", "CiscoSystems"]


# define optional keys of a record structure
class UserRecord(UserRecordKeys, total=False):
    name: str
    age: int


def main() -> None:
    users_table = DataTable[UserRecord]()
    users_table.add_record(
        {
            "email": "john_student@gmail.com",
            "company": "IBM",
            "name": "John",
            "age": 34,
        },
        {
            "email": "mary@gmail.com",
            "company": "CiscoSystems",
            "name": "Mary",
            "age": 34,
        },
    )

    print("Get John's record:")
    print(users_table.get_record(0))

    print("All records as a list:")
    print(list(users_table.get_records()))

    print("Find record with name=Mary:")
    print(users_table.filter_records({"name": "Mary"}).get_record(0))


if __name__ == "__main__":
    main()
