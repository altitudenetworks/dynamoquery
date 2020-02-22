# Dynamo Query

[![PyPI - dynamo-query](https://img.shields.io/pypi/v/dynamo-query.svg?color=blue&label=dynamo-query)](https://pypi.org/project/dynamo-query)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dynamo-query.svg?color=blue)](https://pypi.org/project/dynamo-query)
[![Coverage](https://img.shields.io/codecov/c/github/altitudenetworks/dynamo-query)](https://codecov.io/gh/altitudenetworks/dynamo-query)

Helper for building Boto3 DynamoDB queries.

- [Dynamo Query](#dynamo-query)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Versioning](#versioning)

## Installation

```python
python -m pip install dynamo-query
```

## Usage

### DynamoQuery

```python
import boto3

from dynamo_query import DynamoQuery, DataTable

table_resource = boto3.resource("dynamodb").Table('people')
query = DynamoQuery.build_scan(
    filter_expression=ConditionExpression('first_name') & ('last_name', 'in'),
).limit(
    5,
).projection(
    'first_name', 'last_name', 'age',
).table(
    table_resource=table_resource,
    table_keys=('pk', ),
)
...

# simple query
data = {
    'first_name': 'John',
    'last_name': ['Cena', 'Doe', 'Carmack'],
}

result_data_table = query.execute_dict(data)
for record in result_data_table.get_records():
    print(record)

# batch get
data_table = DataTable.create().add_record(
    {"pk": "my_pk"},
    {"pk": "my_pk2"},
    {"pk": "my_pk3"},
)

result_data_table = query.execute(data_table)
for record in result_data_table.get_records():
    print(record)
```

### DynamoTable

```python
from typing_extensions import TypedDict
from dynamo_query import DynamoTable

# first, define your record
class UserRecord(TypedDict, total=False):
    pk: str
    email: str
    name: str
    points: int


# Create your dynamo table manager with your record class
class MyTable(DynamoTable[UserRecord]):
    # provide a set of your table keys
    table_keys = {'pk'}

    # use this property to define your table name
    @property
    def table_name(self) -> str:
        return "my_table"

    # define how to get PK from a record
    def get_partition_key(self, record: UserRecord) -> str:
        return record["email"]

    # we do not have a sort key in our table
    def get_sort_key(self, record: UserRecord) -> None:
        return None

# okay, let's start using our manager
my_table = MyTable()

# add a new record to your table
my_table.upsert_record({
    "email": "user@gmail.com",
    "name": "John User",
    "points": 12,
})

# and output all the records
for record in my_table.scan():
    print(record)
```

## Development

Install dependencies with [pipenv](https://github.com/pypa/pipenv)

```bash
python -m pip install pipenv
pipenv install -d

# generate boto3 stubs index
python -m mypy_boto3
```

Enable `pylint` and `mypy` checks in your IDE.

Run unit tests and linting.

```bash
./scripts/before_commit.sh
```

Add false-positive unused entities to `vulture` whitelist

```bash
vulture dynamo_query --make-whitelist > vulture_whitelist.txt
```

## Versioning

`dynamo_query` version follows [Semantic Versioning](https://semver.org/).
