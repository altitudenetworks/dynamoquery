# DynamoQuery

[![PyPI - dynamoquery](https://img.shields.io/pypi/v/dynamoquery.svg?color=blue&label=dynamoquery)](https://pypi.org/project/dynamoquery)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dynamoquery.svg?color=blue)](https://pypi.org/project/dynamoquery)
[![Coverage](https://img.shields.io/codecov/c/github/altitudenetworks/dynamoquery)](https://codecov.io/gh/altitudenetworks/dynamoquery)

Helper for building Boto3 DynamoDB queries.

- [DynamoQuery](#dynamoquery)
  - [Installation](#installation)
  - [Usage](#usage)
    - [DynamoQuery](#dynamoquery-1)
    - [DynamoTable](#dynamotable)
  - [Development](#development)
    - [VSCode](#vscode)
    - [PyCharm](#pycharm)
  - [Versioning](#versioning)

## Installation

```python
python -m pip install dynamoquery
```

## Usage

You can find commented usage examples in [examples](https://github.com/altitudenetworks/dynamoquery/tree/master/examples) directory.

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
from typing import Optional
from dynamo_query import DynamoTable, DynamoDictClass

# first, define your record
class UserRecord(DynamoDictClass):
    pk: str
    email: str
    name: str
    points: Optional[int] = None

    @DynamoDictClass.compute_key("pk")
    def get_pk(self) -> str:
        return self.email


# Create your dynamo table manager with your record class
class UserTable(DynamoTable[UserRecord]):
    # provide a set of your table keys
    table_keys = {'pk'}
    record_class = UserRecord

    # use this property to define your table resource
    @property
    def table(self) -> Any:
        return boto3.resource("dynamodb").Table("user_table")


# okay, let's start using our manager
user_table = UserTable()

# add a new record to your table
user_table.upsert_record(
    UserRecord(
        email="user@gmail.com",
        name="John User",
        age=12,
    )
)

# and output all the records
for user_record in user_table.scan():
    print(user_record)
```

## Development

Install dependencies with [pipenv](https://github.com/pypa/pipenv)

```bash
python -m pip install pipenv
pipenv install -d
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

### VSCode

Recommended `.vscode/settings.json`

```json
{
  "python.pythonPath": "<pipenv_path>/bin/python",
  "python.linting.pylintEnabled": true,
  "python.linting.enabled": true,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black"
}
```

### PyCharm

- Install `mypy` unofficial extension
- Install `black`extension, enable format on save
- Run `pylint` on save

## Versioning

`dynamo_query` version follows [Semantic Versioning](https://semver.org/).
