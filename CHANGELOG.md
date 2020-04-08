# Change Log

All notable changes to this project are documented on [Releases](https://github.com/altitudenetworks/dynamoquery/releases) page.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

[Released]

# [Released]

## [1.0.2] - 2020-04-08

### Fixed

- `clear_table` error if `partition_key` prefix is used
- On fail, requests are repeated 5 times (was 3)
- Check for valid operators in `query` oprtaion

