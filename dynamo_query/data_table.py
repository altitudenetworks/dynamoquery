from collections import UserDict, defaultdict
from copy import copy, deepcopy
from typing import (
    Any,
    DefaultDict,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

from dynamo_query.dynamo_query_types import RecordType
from dynamo_query.sentinel import SentinelValue

_RecordType = TypeVar("_RecordType", bound=RecordType)
_R = TypeVar("_R", bound="DataTable")


__all__ = (
    "DataTable",
    "DataTableError",
)


class DataTableError(BaseException):
    """
    Main error for `DataTable` class.
    """


class DataTable(Generic[_RecordType], UserDict):
    """
    Dictionary that has lists as values

    Examples:

        ```python
        data_table = DataTable({'a': [1, 2, 3], 'b': [1]})
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

    Arguments:
        base_dict -- Initial dict, should be compatible with `DataTable` format

    Attributes:
        NOT_SET -- `SentinelValue` to use for missing record values.
        NOT_SET_RESOLVED_VALUE -- A value to replace missing values on getting records.
    """

    NOT_SET = SentinelValue("NOT_SET")
    NOT_SET_RESOLVED_VALUE: Any = None

    @overload
    def __init__(
        self: "DataTable[RecordType]",
        base_dict: Optional[Dict[str, List[Any]]] = ...,
        record_class: None = ...,
    ) -> None:
        ...

    @overload
    def __init__(
        self: "DataTable[_RecordType]",
        base_dict: Optional[Dict[str, List[Any]]] = ...,
        record_class: Type[_RecordType] = ...,
    ) -> None:
        ...

    def __init__(
        self,
        base_dict: Optional[Dict[str, List[Any]]] = None,
        record_class: Optional[Type[_RecordType]] = None,
    ) -> None:
        super().__init__()
        self.record_class: Type[_RecordType] = record_class or dict  # type: ignore
        if base_dict:
            if not isinstance(base_dict, dict):
                raise DataTableError(
                    f"DataTable base dict can only be a dict, got {base_dict} instead"
                )
            for key, value in base_dict.items():
                self._extend_key(key, value)

    @classmethod
    def create(cls: Type[_R], base_dict: Optional[Dict[str, List[Any]]] = None) -> _R:
        """
        Create a DataTable with untyped dicts as records.

        Shorthand to `DataTable[Dict[str, Any]]()`.

        Arguments:
            base_dict -- Initial dict, should be compatible with `DataTable` format.

        Returns:
            A new DataTable instance.
        """
        return cls(base_dict)

    def __copy__(self: _R) -> _R:
        return self.__class__(copy(self.as_defaultdict()), record_class=self.record_class)

    def __deepcopy__(self: _R, memo: Any) -> _R:
        return self.__class__(deepcopy(self.as_defaultdict()), record_class=self.record_class)

    def __bool__(self) -> bool:
        return self.max_length > 0

    def _extend_key(self, key: str, values: List) -> None:
        if not isinstance(values, list):
            raise DataTableError(f"DataTable values can only be lists, got {values} instead")

        if not key in self:
            self[key] = list()
        self[key].extend(values)

    def extend(self: _R, *extra_dicts: Dict[str, List[Any]]) -> _R:
        """
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

        Arguments:
            extra_dicts -- `DtaTable`-like dicts

        Returns:
            Itself, so this method can be chained to another.
        """
        for extra_dict in extra_dicts:
            if not isinstance(extra_dict, dict):
                raise DataTableError(
                    f"DataTable extend dicts can only be dicts, got {extra_dict} instead"
                )
            for key in extra_dict.keys():
                self._extend_key(key, extra_dict[key])

        return self

    def append(self: _R, key: str, values: List) -> _R:
        """
        Append `values` to specified `key` value

        ```python
        base_dict = {'a': [1, 2], 'b': [3]}
        DataTable(base_dict).append('a', [5, 6]) # DataTable({'a': [1, 2, 5, 6], 'b': [3]})
        DataTable(base_dict).append('c', [5, 6]) # DataTable({'a': [1, 2], 'b': [3], 'c': [5, 6]})
        ```

        Arguments:
            key -- Key of dict to append values to
            values -- List of values to append

        Returns:
            Itself, so this method can be chained to another.
        """
        return self.extend({key: values})

    def get_lengths(self) -> List[int]:
        """
        Get lengths of all values as a list

        ```python
        DataTable({'a': [1, 2], 'b': [3, 4]}).get_lengths() # [2, 2]
        DataTable({'a': [1, 2], 'b': [3]}).get_lengths() # [2, 1]
        DataTable({'a': []}).get_lengths() # [0]
        DataTable({}).get_lengths() # []
        ```

        Returns:
            List with all rows lenghts.
        """
        return [len(x) for x in self.values()]

    @property
    def max_length(self) -> int:
        """
        Maximum length of values

        ```python
        DataTable({'a': [1, 2], 'b': [3, 4]}).max_length # 2
        DataTable({'a': [1, 2], 'b': [3]}).max_length # 2
        DataTable({'a': []}).max_length # 0
        DataTable({}).max_length # 0
        ```

        Returns:
            Lenght of the longest row.
        """
        return max(self.get_lengths(), default=0)

    @property
    def min_length(self) -> int:
        """
        Minimum length of values

        ```python
        DataTable({'a': [1, 2], 'b': [3, 4]}).min_length # 2
        DataTable({'a': [1, 2], 'b': [3]}).min_length # 1
        DataTable({'a': []}).min_length # 0
        DataTable({}).min_length # 0
        ```

        Returns:
            Lenght of the shortest row.
        """
        return min(self.get_lengths(), default=0)

    def is_normalized(self) -> bool:
        """
        Check if all values have the same length.

        ```python
        DataTable({'a': [1, 2], 'b': [3, 4]}).is_normalized() # True
        DataTable({'a': [1, 2], 'b': [3]}).is_normalized() # False
        DataTable({}).is_normalized() # True
        ```

        Returns:
            True if all rows have the same length
        """
        return self.min_length == self.max_length

    def resolve_not_set_value(
        self, column_name: str, record_index: int  # pylint: disable=unused-argument
    ) -> Any:
        """
        Get a value to use for missing values.
        Override this methd in a subclass to use a different behavior.

        Arguments:
            column_name -- Column this value belong to.
        """
        return self.NOT_SET_RESOLVED_VALUE

    def normalize(self: _R) -> _R:
        """
        Normalize all items to `max_length` using default value.

        ```python
        data_table = DataTable({'a': [1, 2], 'b': [3], 'c': []})
        data_table.normalize() # DataTable({'a': [1, 2], 'b': [3, None], 'c': [None, None]})
        ```

        Arguments:
            default -- Default_value to extend rows

        Returns:
            Itself, so this method can be chained to another.
        """
        max_length = self.max_length
        for value in self.values():
            value_length = len(value)
            value.extend([self.NOT_SET] * (max_length - value_length))

        return self

    def filter_keys(self: _R, keys: Iterable[str]) -> _R:
        """
        Create a new `DataTable` instance only with keys listed it `keys`

        ```python
        data_table = DataTable({'a': [1, 2], 'b': [3, 4]})
        data_table.filter_keys(['a', 'c']) # DataTable({'a': [1, 2]})
        data_table.filter_keys(data_table.keys()) # DataTable({'a': [1, 2], 'b': [3, 4]})
        data_table.filter_keys([]) # DataTable({})
        ```

        Arguments:
            filter_keys -- List of keys to copy to a new dict.

        Returns:
            A copy of original `DataTable` with matching keys
        """
        result = self.__class__(record_class=self.record_class)
        for key, value in self.items():
            if key in keys:
                result.append(key, value)

        return result

    def as_defaultdict(self) -> DefaultDict[str, List[Any]]:
        """
        Return unwrapped defaultdict(list)

        ```python
        data_table = DataTable({'a': [1, 2], 'b': [3, 4]})
        data_table.as_defaultdict() # defaultdict(<class 'list'>, {'a': [1, 2], 'b': [3, 4]})
        ```

        Returns:
            `defaultdict(list)` with original `DataTable` data.
        """
        new_item: DefaultDict[str, List[Any]] = defaultdict(list)
        for key, value in self.items():
            new_item[key].extend(value)

        return new_item

    def get_records(self) -> Iterator[_RecordType]:
        """
        Generator for all records with keys in DataTable.

        ```python
        data_table = DataTable({'a': [1, 2], 'b': [3, 4]})
        for record in data_table.get_records():
            record # {'a': 1, 'b': 3}, then {'a': 2, 'b': 4}
        ```

        Yields:
            Dict with original `DataTable` keys and corresponding values.
        """
        for record_index in range(self.max_length):
            yield self.get_record(record_index)

    def get_record(self, record_index: int) -> _RecordType:
        """
        Get one record of DataTable by `record_index` as dict of `{key: value}`.
        Not set values are resolved to `NOT_SET_RESOLVED_VALUE` by
        `DataTable.resolve_not_set_value` method.

        ```python
        data_table = DataTable({'a': [1, 2], 'b': [3, 4]})
        data_table.get_record(0) # {'a': 1, 'b': 3}
        data_table.get_record(1) # {'a': 2, 'b': 4}
        data_table.get_record(2) # DataTableError
        ```

        Arguments:
            record_index -- index of record, starting with 0

        Returns:
            Dict with original `DataTable` keys and corresponding values.
        """
        if not self.is_normalized():
            raise DataTableError(
                "Cannot get records from not normalized table. Use `normalize` method."
            )

        if record_index >= self.max_length or record_index < 0:
            raise DataTableError(
                f"Cannot get record {record_index}, DataTable has {self.max_length} records."
            )

        result: Dict[str, Any] = {}
        for key, value in self.items():
            record_value = value[record_index]
            if record_value is self.NOT_SET:
                record_value = self.resolve_not_set_value(
                    column_name=key, record_index=record_index
                )
            result[key] = record_value

        return self._convert_record(result)

    def filter_records(self: _R, query: Dict[str, Any]) -> _R:
        """
        Create a new `DataTable` instance with records that match `query`

        ```python
        data_table = DataTable({'a': [1, 2, 1], 'b': [3, 4, 5], 'c': [1]})
        data_table.filter_records({'a': 1}) # DataTable({'a': [1, 1], 'b': [3, 5], 'c': [1, None]})
        data_table.filter_records({'a': 2}) # DataTable({'a': [2], 'b': [4], 'c': [None]})
        data_table.get_record({'c': 2}) # DataTable({'a': [], 'b': [], 'c': []})
        data_table.get_record({'d': 1}) # DataTable({'a': [], 'b': [], 'c': []})
        ```

        Arguments:
            query -- Query in format `{<key1>: <value1>, <key2>: <value2>}`

        Returns:
            A copy of original `DataTable` with matching records
        """
        if not self.is_normalized():
            raise DataTableError("Cannot filter not normalized table. Use `normalize` method.")

        result = self.__class__({key: [] for key in self.keys()}, record_class=self.record_class)
        for record in self.get_records():
            record_match = True
            for lookup_key, lookup_value in query.items():
                if record.get(lookup_key) != lookup_value:
                    record_match = False
                    break

            if record_match:
                result.extend({key: [value] for key, value in record.items()})

        return result

    def _convert_record(self, record: Union[_RecordType, Dict]) -> _RecordType:
        # pylint: disable=isinstance-second-argument-not-valid-type
        if self.record_class and not isinstance(record, self.record_class):
            # pylint: disable=not-callable
            return self.record_class(record)  # type: ignore

        return record  # type: ignore

    def add_record(self: _R, *records: Union[Dict, _RecordType]) -> _R:
        """
        Add a new record to existing data and normalizes it after each record add.

        ```python
        data_table = DataTable({'a': [1], 'b': [3]})
        data_table.add_record({'a': 5, 'c': 4}, {'c': 5})
        data_table # DataTable({'a': [1, 5], 'b': [3], 'c': [4, 5]})
        ```

        Arguments:
            records -- One or more dicts to add.

        Returns:
            Itself, so this method can be chained to another.
        """
        if not self.is_normalized():
            raise DataTableError(
                "Cannot add records to not normalized table. Use `normalize` method."
            )

        for record in records:
            record = self._convert_record(record)

            row_length = self.max_length
            for key, value in record.items():
                if key not in self.get_column_names():
                    self[key] = [self.NOT_SET] * row_length
                self.append(key, [value])
            self.normalize()

        return self

    def get_column(self, column_name: str) -> List[Any]:
        """
        Return all column values.

        Not set values are resolved to `NOT_SET_RESOLVED_VALUE` by
        `DataTable.resolve_not_set_value` method.

        ```python
        data_table = DataTable({'a': [1, 3], 'b': [2, DataTable.NOT_SET], 'c': []}).normalize()
        data_table.get_column('a') # [1, 3]
        data_table.get_column('b') # [2, None]
        data_table.get_column('c') # [None, None]
        data_table.get_column('d') # [None, None]
        ```

        Arguments:
            column_name -- Column name.

        Returns:
            A list of column values.

        Raises:
            DataTableError -- If table is not normalized.
        """
        if not self.is_normalized():
            raise DataTableError(
                "Cannot get column to not normalized table. Use `normalize` method."
            )

        result = []
        if not self.has_column(column_name):
            for record_index in range(self.max_length):
                result.append(
                    self.resolve_not_set_value(column_name=column_name, record_index=record_index)
                )
            return result
        column_values = self.get(column_name) or []
        for record_index, column_value in enumerate(column_values):
            if column_value is self.NOT_SET:
                column_value = self.resolve_not_set_value(
                    column_name=column_name, record_index=record_index
                )
            result.append(column_value)

        return result

    def has_column(self, *column_names: str) -> bool:
        """
        Check if all columns with `column_names` exist.

        ```python
        data_table = DataTable({'a': [1], 'b': [2], 'c': []}).normalize()
        data_table.has_column('a') # True
        data_table.has_column('b') # True
        data_table.has_column('c') # True
        data_table.has_column('d') # False
        ```

        Arguments:
            column_names -- One or more column names for check.

        Returns:
            True if check is successful.
        """
        for column_name in column_names:
            if column_name not in self.get_column_names():
                return False

        return True

    def has_set_column(self, *column_names: str) -> bool:
        """
        Check if all columns with `column_names` exist and have all values set.

        ```python
        data_table = DataTable({'a': [1], 'b': [2], 'c': []}).normalize()
        data_table.has_set_column('a') # True
        data_table.has_set_column('b') # True
        data_table.has_set_column('c') # False
        data_table.has_set_column('d') # False
        ```

        Arguments:
            column_names -- One or more column names for check.

        Returns:
            True if check is successful.
        """
        for column_name in column_names:
            values = self.get(column_name)
            if values is None:
                return False
            if self.NOT_SET in values:
                return False

        return True

    def add_table(self: _R, *data_tables: _R) -> _R:
        """
        Add all records from another `DataTable` to existing one.
        All tables have to be normalized.

        ```python
        data_table = DataTable({'a': [1], 'b': [2]})
        data_table2 = DataTable({'a': [3], 'b': [4]})
        data_table.add_table(data_table2)
        data_table # DataTable({'a': [1, 3], 'b': [2, 4]})
        ```

        Arguments:
            data_tables -- One or more `DataTable` to add.

        Returns:
            Itself, so this method can be chained to another.

        Raises:
            DataTableError -- If one of the tables are not normalized.
        """
        if not self.is_normalized():
            raise DataTableError(
                "Cannot add table to not normalized table. Use `normalize` method."
            )

        for data_table in data_tables:
            if not data_table.is_normalized():
                raise DataTableError("Cannot add not normalized table. Use `normalize` method.")

        for data_table in data_tables:
            for record in data_table.get_records():
                self.add_record(record)

        return self

    def get_column_names(self) -> List[str]:
        """
        Get all column names.

        ```python
        data_table = DataTable({'a': [1], 'b': [DataTable.NOT_SET], 'c': []})
        data_table.get_column_names() # ['a', 'b', 'c']
        ```

        Returns:
            A list of column names.
        """
        return list(self.keys())

    def get_set_column_names(self) -> List[str]:
        """
        Get column names that have no NOT_SET values.

        ```python
        data_table = DataTable({'a': [1], 'b': [DataTable.NOT_SET], 'c': []})
        data_table.get_set_column_names() # ['a', 'c']
        data_table.normalize()
        data_table.get_set_column_names() # ['a']
        ```

        Returns:
            A list of column names.
        """
        result = []
        for column_name, values in self.items():
            if self.NOT_SET not in values:
                result.append(column_name)

        return result

    def set(self: _R, column_name: str, record_index: int, value: Any) -> _R:
        """
        Set `value` in-place for `column_name` and `record_index`.

        ```python
        data_table = DataTable({'a': [1, 2], 'b': [DataTable.NOT_SET]})
        data_table.set('a', 1, 'value_a').set('b', 0, 'value_b')
        data_table # DataTable({'a': [1, 'value_a'], 'b': ['value_b']})

        data_table.set('b', 1, 'value_b') # DataTableError
        data_table.set('c', 0, 'value_c') # DataTableError
        ```

        Returns:
            Itself, so this method can be chained to another.

        Raises:
            DataTableError -- If `column_name` does not exist or has no `record_index`.
        """
        if not self.has_column(column_name):
            raise DataTableError(f"Column {column_name} does not exist")

        try:
            self[column_name][record_index] = value
        except IndexError:
            raise DataTableError(f"Column {column_name} does not have index {record_index}")

        return self

    def __iter__(self) -> Iterator[_RecordType]:
        return self.get_records()

    def keys(self) -> Iterator[str]:  # type: ignore
        """
        Iterate over keys of a base dict.

        Example:

            ```python
            d = DataTable({"a": [1, 2], "b": [3, 4]})
            for item in d.keys():
                print(item) # "a", then "b"
            ```

        Returns:
            An iterator over base dict keys.
        """
        return super().__iter__()

    def values(self) -> Iterator[List[Any]]:  # type: ignore
        """
        Iterate over values of a base dict.

        Example:

            ```python
            d = DataTable({"a": [1, 2], "b": [3, 4]})
            for item in d.values():
                print(item) # [1, 2], then [3, 4]
            ```

        Returns:
            An iterator over base dict values.
        """
        for key in super().__iter__():
            yield self[key]

    def items(self) -> Iterator[Tuple[str, List[Any]]]:  # type: ignore
        """
        Iterate over items of a base dict.

        Example:

            ```python
            d = DataTable({"a": [1, 2], "b": [3, 4]})
            for item in d.items():
                print(item) # ("a", [1, 2]), then ("b", [3, 4])
            ```

        Returns:
            An iterator over base dict items.
        """
        for key in super().__iter__():
            yield (key, self[key])

    def copy(self: _R) -> _R:
        """
        Equivalent of `copy`

        Returns:
            A new instance.
        """
        return self.__copy__()
