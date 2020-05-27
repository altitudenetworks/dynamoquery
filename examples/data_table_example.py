"""
Usage examples for `DataTable` class.
"""
from typing import Optional

from dynamo_query.data_table import DataTable
from dynamo_query.dynamo_record import DynamoRecord


# define keys of a record structure
class UserRecord(DynamoRecord):
    email: str
    company: str = "IBM"
    name: Optional[str] = None
    age: Optional[int] = None


def main() -> None:
    users_table = DataTable[UserRecord](record_class=UserRecord)
    users_table.add_record(
        {"email": "john_student@gmail.com", "name": "John", "age": 34},
        {"email": "mary@gmail.com", "company": "CiscoSystems", "name": "Mary", "age": 34},
    )

    print("Get John's record:")
    print(users_table.get_record(0))

    print("All records as a list:")
    print(list(users_table.get_records()))

    print("Find record with name=Mary:")
    print(users_table.filter_records({"name": "Mary"}).get_record(0))


if __name__ == "__main__":
    main()
