# Boto3Retrier

> Auto-generated documentation for [dynamo_query.boto3_retrier](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/boto3_retrier.py) module.

https://codereview.stackexchange.com/questions/133310/python-decorator-for-retrying-w-exponential-backoff
https://developers.google.com/admin-sdk/directory/v1/limits#backoff

- [dynamo-query](../README.md#dynamo-query) / [Modules](../MODULES.md#dynamo-query-modules) / [Dynamo Query](index.md#dynamo-query) / Boto3Retrier
    - [BatchUnprocessedItemsError](#batchunprocesseditemserror)
    - [Boto3Retrier](#boto3retrier)
        - [Boto3Retrier.backoff](#boto3retrierbackoff)
        - [Boto3Retrier.doubling_backoff](#boto3retrierdoubling_backoff)
        - [Boto3Retrier.get_exception_scope](#boto3retrierget_exception_scope)
        - [Boto3Retrier().handle_exception](#boto3retrierhandle_exception)
        - [Boto3Retrier.no_backoff](#boto3retrierno_backoff)

## BatchUnprocessedItemsError

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/boto3_retrier.py#L34)

```python
class BatchUnprocessedItemsError(Exception):
    def __init__(unprocessed_items: List[Any], response: Any) -> None:
```

Raise if batch operation has unprocessed items

## Boto3Retrier

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/boto3_retrier.py#L51)

```python
class Boto3Retrier():
    def __init__(
        num_tries: Optional[int] = None,
        delay: Optional[int] = None,
        backoff: Optional[Callable[[int], Generator[int, None, None]]] = None,
        logger: Optional[logging.Logger] = None,
        log_level: Optional[int] = None,
        exceptions_to_catch: Optional[Tuple[Type[BaseException], ...]] = None,
        exceptions_to_suppress: Optional[Tuple[Type[BaseException], ...]] = None,
        fallback_value: Any = NOT_SET,
    ) -> None:
```

A decorator to retry a call on all exceptions except the ones defined in {
exceptions_to_suppress}.
Works with functions and class methods.

```python
class APIClient:
    @Boto3Retrier(num_tries=5)
    def get_items(self):
        ...

@Boto3Retrier(exceptions_to_suppress=(OSError, ))
def read_files():
    ...
```

#### Arguments

- `num_tries` - Number of tries before an expected Exception is raised.
- `delay` - Default delay in seconds between retries.
- `backoff` - Generator that gets original delay and yields delay for retries.
- `logger` - Logger instance. If not passed, logger will be created internally.
- `log_level` - Level of a log message on retry.
- `exceptions_to_catch` - List of expected exceptions. `default_exceptions` is used if None.
- `exceptions_to_suppress` - Tuple of exceptions that should not be retried and raised
                          immediately if fallback_value is not provided.
- `fallback_value` - Return value on fait. If not provided, exception is raised.

#### Attributes

- `NOT_SET` - `tools.sentinel.SentinelValue` for not provided arguments.
- `default_exceptions` - A list of expected exceptions. By default, accepts all.
- `default_num_tries` - Default number of tries - 3
- `default_delay` - Default delay - 1 second
- `default_log_level` - `Logger.ERROR`
- `default_fallback_value` - `NOT_SET`
- `doubling_backoff` - Backoff that doubles delay on each retry.
- `no_backoff` - Backoff that uses start delay on each retry.
- `backoff` - `doubling_backoff` is used

### Boto3Retrier.backoff

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/boto3_retrier.py#L180)

```python
@classmethod
def backoff(start: int) -> Generator[int, None, None]:
```

Override this method in a subclass to use a different backoff generator.
Doubling backoff generator is used.

#### Arguments

- `start` - Starting value of the delay

#### Returns

A generator of delay in seconds.

### Boto3Retrier.doubling_backoff

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/boto3_retrier.py#L148)

```python
@classmethod
def doubling_backoff(start: int) -> Generator[int, None, None]:
```

Generate delay that doubles with each retry in seconds. If start delay is 0,
delay of 1 second is used.

#### Arguments

- `start` - Starting value of the delay

#### Returns

A generator of delay in seconds.

### Boto3Retrier.get_exception_scope

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/boto3_retrier.py#L194)

```python
@staticmethod
def get_exception_scope(exc: BaseException) -> Dict[Text, Any]:
```

Get original method scope from exception object.

#### Arguments

exc - Exception object

#### Returns

A scope as a dict.

### Boto3Retrier().handle_exception

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/boto3_retrier.py#L213)

```python
def handle_exception(exc: BaseException) -> None:
```

Override this method in a subclass to do something on each failed try.
You can access decorated method data from here.

- `self.method` - Decorated method.
- `self.method_parent` - Decorated method parent or None if it is a function.
- `self.method_args` - Arguments for method call.
- `self.method_kwargs` - Keyword arguments for method call.

#### Arguments

- `exc` - Raised exception.

### Boto3Retrier.no_backoff

[[find in source code]](https://github.com/altitudenetworks/dynamo_query/blob/master/dynamo_query/boto3_retrier.py#L165)

```python
@classmethod
def no_backoff(start: int) -> Generator[int, None, None]:
```

Generate the delay duration between each retry in seconds.
Always uses `start` delay.

#### Arguments

- `start` - Starting value of the delay

#### Returns

A generator of delay in seconds.
