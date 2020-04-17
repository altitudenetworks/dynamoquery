# Change Log

All notable changes to this project are documented on [Releases](https://github.com/altitudenetworks/dynamoquery/releases) page.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

# [Released]

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