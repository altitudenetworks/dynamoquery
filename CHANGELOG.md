# Change Log

All notable changes to this project are documented on [Releases](https://github.com/altitudenetworks/dynamoquery/releases) page.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

# [Released]

## [2.4.0] - 2020-06-04

### Added

- `DynamoTable.clear_records` method [#38](https://github.com/altitudenetworks/dynamoquery/pull/38)

### Fixed

- `DynamoTable` class is no longer abstract
- `DictClass` sanitization of initial data happens in the end on all values, even non-set
- `DynamoTable` normalizes records in singular methods
- `DynamoTable.batch_delete` returns correct record type
- `DynamoTable.clear_table` respects `sort_key`/`sort_key_prefix` arguments even if `partition_key` is None (full scan) [#38](https://github.com/altitudenetworks/dynamoquery/pull/38)

## [2.3.0] - 2020-06-02

### Notes

Important info:
- release notes are managed automatically
- do not add new sections, but all sections can be edited, including this one
- always edit release notes before publishing
- on publish all release notes are included to `CHANGELOG.md`

### Added

- `DictClass` record type
- `LooseDictClass` record type
- `DynamoDictClass` record type [#36](https://github.com/altitudenetworks/dynamoquery/pull/36)

### Changed

- Untyped `DynamoTable` uses `LooseDictClass`
- `DataTable` with provided `record_class` does not need explicit typing [#36](https://github.com/altitudenetworks/dynamoquery/pull/36)

### Fixed

- Duplicate items detection in `DynamoTable.batch_delete` [#36](https://github.com/altitudenetworks/dynamoquery/pull/36)

## [2.2.0] - 2020-05-29

### Added

- `DynamoRecord.sanitize` method for all values clean up
- `DynamoRecord.sanitize_key` method for value clean up
- `DynamoRecord.get_key_{key}` custom methods support
- `DynamoRecord.sanitize_key_{key}` custom methods support [#34](https://github.com/altitudenetworks/dynamoquery/pull/34)

### Fixed

- `DynamoRecord` attribute default values are now immutable
- `DynamoRecord` uppercased class attributes no longer affect fields [#34](https://github.com/altitudenetworks/dynamoquery/pull/34)

## [2.1.0] - 2020-05-29

### Added

- `DynamoTable.batch_get_records` that works with iterators
- `DynamoTable.batch_upsert_records` that works with iterators
- `DynamoTable.batch_delete_records` that works with iterators
- `DynamoTable.dynamo_query_class` attribute that allows to use custom `DynamoQuery`
- `DynamoTable.max_batch_size` property for easier subclassing [#28](https://github.com/altitudenetworks/dynamoquery/pull/28)
- `DynamoRecord` UserDict class for class-based
- `record_type` argument to `DataClass` init that accepts any `UserDict`-based classes
- `DynamoTable.get_table_status` method to get current table status
- `DynamoAutoscaler` class [#30](https://github.com/altitudenetworks/dynamoquery/pull/30)
- `DataTable.copy` method [#31](https://github.com/altitudenetworks/dynamoquery/pull/31)

### Changed

- `DynamoTable.clear_table` uses generators to reduce memory usage [#28](https://github.com/altitudenetworks/dynamoquery/pull/28)
- `DataTable.get_record` returns a `record_type` object if it was provided
- `DataTable.get_records` yields `record_type` objects if it was provided
- `DataTable.add_record` processes a `record_type` object if it was provided
- `DynamoTable.create_table` sets `ProvisionedThroughput` arguments
- `DynamoTable.create_table` handles intermediate table states
- `DynamoTable.delete_table` handles intermediate table states
- `DynamoTable.get_partition_key` method is not longer abstract
- `DynamoTable.get_sort_key` method is not longer abstract [#30](https://github.com/altitudenetworks/dynamoquery/pull/30)
- `DataTable.keys` returns an iterator (not compatible with a regular dict)
- `DataTable.values` returns an iterator (not compatible with a regular dict)
- `DataTable.items` returns an iterator (not compatible with a regular dict)
- `DataTable.__iter__` iterates over records (used to be keys) and fails for non-normalized tables
- `DynamoQuery.execute_dict` method's `data` argument made optional
- `DynamoQuery.execute` method's `data_table` argument accepts `Iterable[Dict]` a well as a `DataTable` [#31](https://github.com/altitudenetworks/dynamoquery/pull/31)

### Fixed

- `DynamoTable` is marked as abstract
- `mypy` can correctly use types from this library [#29](https://github.com/altitudenetworks/dynamoquery/pull/29)
- Typing for subclassed `DataTable` [#31](https://github.com/altitudenetworks/dynamoquery/pull/31)
- `typing-extensions` is no longer a direct dependency [#32](https://github.com/altitudenetworks/dynamoquery/pull/32)

## [2.0.0] - 2020-04-17

### Removed

- `Boto3Retrier` class
- `tests/test_boto3_retrier.py` [#23](https://github.com/altitudenetworks/dynamoquery/pull/23)

## [1.2.0] - 2020-04-16

### Changed

- `DataTable` is a regular dictionary, used to be a `defaultdict`

### Fixed

- Circular error due to bad naming

## [1.1.0] - 2020-04-08

### Changed

- `partiton_key` argument is mandatory in `DynamoTable.query`

### Fixed

- `DynamoTable.clear_table` error if `partition_key_prefix` is used
- On fail, requests are repeated 5 times (was 3)
- Check for valid operators in `DynamoTable.query` opertaion