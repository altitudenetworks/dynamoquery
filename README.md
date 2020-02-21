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

## Versioning

`dynamo_query` version follows [Semantic Versioning](https://semver.org/).
