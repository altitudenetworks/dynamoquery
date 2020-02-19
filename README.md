# Dynamo Query

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
    limit=5,
    filter_expression=ConditionExpression('first_name') & ('last_name', 'in'),
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
