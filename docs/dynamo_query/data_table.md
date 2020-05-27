# DataTable

> Auto-generated documentation for [dynamo_query.data_table](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/data_table.py) module.

- [dynamo-query](../README.md#dynamoquery) / [Modules](../MODULES.md#dynamo-query-modules) / [Dynamo Query](index.md#dynamo-query) / DataTable
    - [DataTable](#datatable)
        - [DataTable().add_record](#datatableadd_record)
        - [DataTable().add_table](#datatableadd_table)
        - [DataTable().append](#datatableappend)
        - [DataTable().as_defaultdict](#datatableas_defaultdict)
        - [DataTable.create](#datatablecreate)
        - [DataTable().extend](#datatableextend)
        - [DataTable().filter_keys](#datatablefilter_keys)
        - [DataTable().filter_records](#datatablefilter_records)
        - [DataTable().get_column](#datatableget_column)
        - [DataTable().get_column_names](#datatableget_column_names)
        - [DataTable().get_lengths](#datatableget_lengths)
        - [DataTable().get_record](#datatableget_record)
        - [DataTable().get_records](#datatableget_records)
        - [DataTable().get_set_column_names](#datatableget_set_column_names)
        - [DataTable().has_column](#datatablehas_column)
        - [DataTable().has_set_column](#datatablehas_set_column)
        - [DataTable().is_normalized](#datatableis_normalized)
        - [DataTable().max_length](#datatablemax_length)
        - [DataTable().min_length](#datatablemin_length)
        - [DataTable().normalize](#datatablenormalize)
        - [DataTable().resolve_not_set_value](#datatableresolve_not_set_value)
        - [DataTable().set](#datatableset)
    - [DataTableError](#datatableerror)

## DataTable

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/data_table.py#L35)

```python
class DataTable(Generic[_RecordType], UserDict):
    def __init__(
        base_dict: Optional[Dict[str, List[Any]]] = None,
        record_class: Optional[Type[UserDict]] = None,
    ) -> None:
```

Dictionary that has lists as values

#### Examples

```python
data_table = DataTable.create({'a': [1, 2, 3], 'b': [1]})
data_table.max_length # 3
data_table.min_length # 1
data_table.get_lengths() # [3, 1]
data_table.is_normalized() # False

data_table.append('b', [3, 4])
data_table # {'a': [1, 2, 3], 'b': [1, 3, 4]}
data_table.is_normalized() # True

data_table.extend({'c': [5, 6]})
data_table # {'a': [1, 2, 3], 'b': [1, 3, 4], 'c': [5, 6]}

data_table.normalize()
data_table.is_normalized() # True
data_table # {'a': [1, 2, 3], 'b': [1, 3, 4], 'c': [5, 6, NOT_SET]}

from copy import copy
copy(data_table)  # {'a': [1, 2, 3], 'b': [1, 3, 4], 'c': [5, 6, NOT_SET]}
data_table.filter_keys(['a'])  # {'a': [1, 2, 3]}
data_table.filter_keys(['a']).extend({'b': [4]}).normalize()
data_table  # {'a': [1, 2, 3], 'b': [4, NOT_SET, NOT_SET]}


class MyRecord(TypedDict):
    key: str

typed_data_table = DataTable[MyRecord]()
typed_data_table.add_record({"key": "value"})
```

#### Arguments

- `base_dict` - Initial dict, should be compatible with [DataTable](#datatable) format

#### Attributes

- `NOT_SET` - `SentinelValue` to use for missing record values.
- `NOT_SET_RESOLVED_VALUE` - A value to replace missing values on getting records.

### DataTable().add_record

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/data_table.py#L423)

```python
def add_record(
    *records: Union[Dict, _RecordType],
) -> 'DataTable[_RecordType]':
```

Add a new record to existing data and normalizes it after each record add.

```python
data_table = DataTable({'a': [1], 'b': [3]})
data_table.add_record({'a': 5, 'c': 4}, {'c': 5})
data_table # DataTable({'a': [1, 5], 'b': [3], 'c': [4, 5]})
```

#### Arguments

- `records` - One or more dicts to add.

#### Returns

Itself, so this method can be chained to another.

### DataTable().add_table

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/data_table.py#L553)

```python
def add_table(*data_tables: 'DataTable') -> 'DataTable':
```

Add all records from another [DataTable](#datatable) to existing one.
All tables have to be normalized.

```python
data_table = DataTable({'a': [1], 'b': [2]})
data_table2 = DataTable({'a': [3], 'b': [4]})
data_table.add_table(data_table2)
data_table # DataTable({'a': [1, 3], 'b': [2, 4]})
```

#### Arguments

- `data_tables` - One or more [DataTable](#datatable) to add.

#### Returns

Itself, so this method can be chained to another.

#### Raises

- `DataTableError` - If one of the tables are not normalized.

### DataTable().append

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/data_table.py#L163)

```python
def append(key: str, values: List) -> 'DataTable[_RecordType]':
```

Append `values` to specified `key` value

```python
base_dict = {'a': [1, 2], 'b': [3]}
DataTable(base_dict).append('a', [5, 6]) # DataTable({'a': [1, 2, 5, 6], 'b': [3]})
DataTable(base_dict).append('c', [5, 6]) # DataTable({'a': [1, 2], 'b': [3], 'c': [5, 6]})
```

#### Arguments

- `key` - Key of dict to append values to
- `values` - List of values to append

#### Returns

Itself, so this method can be chained to another.

### DataTable().as_defaultdict

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/data_table.py#L305)

```python
def as_defaultdict() -> DefaultDict[str, List[Any]]:
```

Return unwrapped defaultdict(list)

```python
data_table = DataTable({'a': [1, 2], 'b': [3, 4]})
data_table.as_defaultdict() # defaultdict(<class 'list'>, {'a': [1, 2], 'b': [3, 4]})
```

#### Returns

`defaultdict(list)` with original [DataTable](#datatable) data.

### DataTable.create

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/data_table.py#L99)

```python
@classmethod
def create(
    base_dict: Optional[Dict[str, List[Any]]] = None,
) -> 'DataTable[Dict[str, Any]]':
```

Create a DataTable with untyped dicts as records.

Shorthand to `DataTable[Dict[str, Any]]()`.

#### Arguments

- `base_dict` - Initial dict, should be compatible with [DataTable](#datatable) format.

#### Returns

A new DataTable instance.

### DataTable().extend

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/data_table.py#L133)

```python
def extend(*extra_dicts: Dict[str, List[Any]]) -> 'DataTable[_RecordType]':
```

Extend values lists with values from `extra_dicts`
If some keys are missing from this dict, they will be created.

```python
base_dict = {'a': [1], 'b': [3]}
DataTable(base_dict).extend({'a':  [5, 6]}) # DataTable({'a': [1, 5, 6], 'b': [3]})
DataTable(base_dict).extend({'c': [5, 6]}) # DataTable({'a': [1], 'b': [3], 'c': [5, 6]})
DataTable(base_dict).extend(
    {'a': [1]}, {'c': [1]}
) # DataTable({'a': [1, 1], 'b': [3], 'c': [1]})
```

#### Arguments

- `extra_dicts` - `DtaTable`-like dicts

#### Returns

Itself, so this method can be chained to another.

### DataTable().filter_keys

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/data_table.py#L281)

```python
def filter_keys(keys: Iterable[str]) -> 'DataTable[Dict[str, Any]]':
```

Create a new [DataTable](#datatable) instance only with keys listed it `keys`

```python
data_table = DataTable({'a': [1, 2], 'b': [3, 4]})
data_table.filter_keys(['a', 'c']) # DataTable({'a': [1, 2]})
data_table.filter_keys(data_table.keys()) # DataTable({'a': [1, 2], 'b': [3, 4]})
data_table.filter_keys([]) # DataTable({})
```

#### Arguments

- `filter_keys` - List of keys to copy to a new dict.

#### Returns

A copy of original [DataTable](#datatable) with matching keys

### DataTable().filter_records

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/data_table.py#L379)

```python
def filter_records(query: Dict[str, Any]) -> 'DataTable[_RecordType]':
```

Create a new [DataTable](#datatable) instance with records that match `query`

```python
data_table = DataTable({'a': [1, 2, 1], 'b': [3, 4, 5], 'c': [1]})
data_table.filter_records({'a': 1}) # DataTable({'a': [1, 1], 'b': [3, 5], 'c': [1, None]})
data_table.filter_records({'a': 2}) # DataTable({'a': [2], 'b': [4], 'c': [None]})
data_table.get_record({'c': 2}) # DataTable({'a': [], 'b': [], 'c': []})
data_table.get_record({'d': 1}) # DataTable({'a': [], 'b': [], 'c': []})
```

#### Arguments

- `query` - Query in format `{<key1>: <value1>, <key2>: <value2>}`

#### Returns

A copy of original [DataTable](#datatable) with matching records

### DataTable().get_column

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/data_table.py#L456)

```python
def get_column(column_name: str) -> List[Any]:
```

Return all column values.

Not set values are resolved to `NOT_SET_RESOLVED_VALUE` by
[DataTable().resolve_not_set_value](#datatableresolve_not_set_value) method.

```python
data_table = DataTable({'a': [1, 3], 'b': [2, DataTable.NOT_SET], 'c': []}).normalize()
data_table.get_column('a') # [1, 3]
data_table.get_column('b') # [2, None]
data_table.get_column('c') # [None, None]
data_table.get_column('d') # [None, None]
```

#### Arguments

- `column_name` - Column name.

#### Returns

A list of column values.

#### Raises

- `DataTableError` - If table is not normalized.

### DataTable().get_column_names

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/data_table.py#L589)

```python
def get_column_names() -> List[str]:
```

Get all column names.

```python
data_table = DataTable({'a': [1], 'b': [DataTable.NOT_SET], 'c': []})
data_table.get_column_names() # ['a', 'b', 'c']
```

#### Returns

A list of column names.

### DataTable().get_lengths

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/data_table.py#L182)

```python
def get_lengths() -> List[int]:
```

Get lengths of all values as a list

```python
DataTable({'a': [1, 2], 'b': [3, 4]}).get_lengths() # [2, 2]
DataTable({'a': [1, 2], 'b': [3]}).get_lengths() # [2, 1]
DataTable({'a': []}).get_lengths() # [0]
DataTable({}).get_lengths() # []
```

#### Returns

List with all rows lenghts.

### DataTable().get_record

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/data_table.py#L339)

```python
def get_record(record_index: int) -> _RecordType:
```

Get one record of DataTable by `record_index` as dict of `{key: value}`.
Not set values are resolved to `NOT_SET_RESOLVED_VALUE` by
[DataTable().resolve_not_set_value](#datatableresolve_not_set_value) method.

```python
data_table = DataTable({'a': [1, 2], 'b': [3, 4]})
data_table.get_record(0) # {'a': 1, 'b': 3}
data_table.get_record(1) # {'a': 2, 'b': 4}
data_table.get_record(2) # DataTableError
```

#### Arguments

- `record_index` - index of record, starting with 0

#### Returns

Dict with original [DataTable](#datatable) keys and corresponding values.

### DataTable().get_records

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/data_table.py#L323)

```python
def get_records() -> Iterator[_RecordType]:
```

Generator for all records with keys in DataTable.

```python
data_table = DataTable({'a': [1, 2], 'b': [3, 4]})
for record in data_table.get_records():
    record # {'a': 1, 'b': 3}, then {'a': 2, 'b': 4}
```

#### Yields

Dict with original [DataTable](#datatable) keys and corresponding values.

### DataTable().get_set_column_names

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/data_table.py#L603)

```python
def get_set_column_names() -> List[str]:
```

Get column names that have no NOT_SET values.

```python
data_table = DataTable({'a': [1], 'b': [DataTable.NOT_SET], 'c': []})
data_table.get_set_column_names() # ['a', 'c']
data_table.normalize()
data_table.get_set_column_names() # ['a']
```

#### Returns

A list of column names.

### DataTable().has_column

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/data_table.py#L502)

```python
def has_column(*column_names: str) -> bool:
```

Check if all columns with `column_names` exist.

```python
data_table = DataTable({'a': [1], 'b': [2], 'c': []}).normalize()
data_table.has_column('a') # True
data_table.has_column('b') # True
data_table.has_column('c') # True
data_table.has_column('d') # False
```

#### Arguments

- `column_names` - One or more column names for check.

#### Returns

True if check is successful.

### DataTable().has_set_column

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/data_table.py#L526)

```python
def has_set_column(*column_names: str) -> bool:
```

Check if all columns with `column_names` exist and have all values set.

```python
data_table = DataTable({'a': [1], 'b': [2], 'c': []}).normalize()
data_table.has_set_column('a') # True
data_table.has_set_column('b') # True
data_table.has_set_column('c') # False
data_table.has_set_column('d') # False
```

#### Arguments

- `column_names` - One or more column names for check.

#### Returns

True if check is successful.

### DataTable().is_normalized

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/data_table.py#L232)

```python
def is_normalized() -> bool:
```

Check if all values have the same length.

```python
DataTable({'a': [1, 2], 'b': [3, 4]}).is_normalized() # True
DataTable({'a': [1, 2], 'b': [3]}).is_normalized() # False
DataTable({}).is_normalized() # True
```

#### Returns

True if all rows have the same length

### DataTable().max_length

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/data_table.py#L198)

```python
@property
def max_length() -> int:
```

Maximum length of values

```python
DataTable({'a': [1, 2], 'b': [3, 4]}).max_length # 2
DataTable({'a': [1, 2], 'b': [3]}).max_length # 2
DataTable({'a': []}).max_length # 0
DataTable({}).max_length # 0
```

#### Returns

Lenght of the longest row.

### DataTable().min_length

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/data_table.py#L215)

```python
@property
def min_length() -> int:
```

Minimum length of values

```python
DataTable({'a': [1, 2], 'b': [3, 4]}).min_length # 2
DataTable({'a': [1, 2], 'b': [3]}).min_length # 1
DataTable({'a': []}).min_length # 0
DataTable({}).min_length # 0
```

#### Returns

Lenght of the shortest row.

### DataTable().normalize

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/data_table.py#L259)

```python
def normalize() -> 'DataTable':
```

Normalize all items to [DataTable().max_length](#datatablemax_length) using default value.

```python
data_table = DataTable({'a': [1, 2], 'b': [3], 'c': []})
data_table.normalize() # DataTable({'a': [1, 2], 'b': [3, None], 'c': [None, None]})
```

#### Arguments

- `default` - Default_value to extend rows

#### Returns

Itself, so this method can be chained to another.

### DataTable().resolve_not_set_value

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/data_table.py#L247)

```python
def resolve_not_set_value(column_name: str, record_index: int) -> Any:
```

Get a value to use for missing values.
Override this methd in a subclass to use a different behavior.

#### Arguments

- `column_name` - Column this value belong to.

### DataTable().set

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/data_table.py#L624)

```python
def set(
    column_name: str,
    record_index: int,
    value: Any,
) -> 'DataTable[_RecordType]':
```

Set `value` in-place for `column_name` and `record_index`.

```python
data_table = DataTable({'a': [1, 2], 'b': [DataTable.NOT_SET]})
data_table.set('a', 1, 'value_a').set('b', 0, 'value_b')
data_table # DataTable({'a': [1, 'value_a'], 'b': ['value_b']})

data_table.set('b', 1, 'value_b') # DataTableError
data_table.set('c', 0, 'value_c') # DataTableError
```

#### Returns

Itself, so this method can be chained to another.

#### Raises

- `DataTableError` - If `column_name` does not exist or has no `record_index`.

## DataTableError

[[find in source code]](https://github.com/altitudenetworks/dynamoquery/blob/master/dynamo_query/data_table.py#L29)

```python
class DataTableError(BaseException):
```

Main error for [DataTable](#datatable) class.
