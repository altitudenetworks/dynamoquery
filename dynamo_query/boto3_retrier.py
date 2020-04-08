#!/usr/bin/env python

"""
https://codereview.stackexchange.com/questions/133310/python-decorator-for-retrying-w-exponential-backoff
https://developers.google.com/admin-sdk/directory/v1/limits#backoff
"""

import time
import functools
import logging
from typing import (
    Generator,
    Callable,
    Optional,
    Any,
    Dict,
    Type,
    Tuple,
    List,
    TypeVar,
    cast,
)

from botocore.exceptions import ClientError

from dynamo_query.utils import pluralize, get_nested_item
from dynamo_query.sentinel import SentinelValue


FunctionType = TypeVar("FunctionType", bound=Callable[..., Any])


class BatchUnprocessedItemsError(Exception):
    "Raise if batch operation has unprocessed items"

    def __init__(self, unprocessed_items: List[Any], response: Any) -> None:
        """
        Arguments:
            unprocessed_items -- List of unprocessed items
            response -- Raw AWS response
        """
        self.unprocessed_items = unprocessed_items
        self.response = response
        super(BatchUnprocessedItemsError, self).__init__()

    def __str__(self) -> Any:
        return self.response


class Boto3Retrier:
    """
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

    Arguments:
        num_tries -- Number of tries before an expected Exception is raised.
        delay -- Default delay in seconds between retries.
        backoff -- Generator that gets original delay and yields delay for retries.
        logger -- Logger instance. If not passed, logger will be created internally.
        log_level -- Level of a log message on retry.
        exceptions_to_catch -- List of expected exceptions. `default_exceptions` is used if None.
        exceptions_to_suppress -- Tuple of exceptions that should not be retried and raised
                                  immediately if fallback_value is not provided.
        fallback_value -- Return value on fait. If not provided, exception is raised.

    Attributes:
        NOT_SET -- `SentinelValue` for not provided arguments.
        default_exceptions -- A list of expected exceptions. By default, accepts all.
        default_num_tries -- Default number of tries - 5
        default_delay -- Default delay - 1 second
        default_log_level -- `Logger.ERROR`
        default_fallback_value -- `NOT_SET`
        doubling_backoff -- Backoff that doubles delay on each retry.
        no_backoff -- Backoff that uses start delay on each retry.
        backoff -- `doubling_backoff` is used
    """

    NOT_SET: Any = SentinelValue("NOT_SET")
    default_num_tries = 5
    default_delay = 1
    default_log_level = logging.ERROR
    default_fallback_value: Any = NOT_SET
    retry_error_codes = (
        "ProvisionedThroughputExceededException",
        "ThrottlingException",
    )
    default_exceptions: Tuple[Type[BaseException], ...] = (
        ClientError,
        BatchUnprocessedItemsError,
    )

    ###################
    def __init__(
        self,
        num_tries: Optional[int] = None,
        delay: Optional[int] = None,
        backoff: Optional[Callable[[int], Generator[int, None, None]]] = None,
        logger: Optional[logging.Logger] = None,
        log_level: Optional[int] = None,
        exceptions_to_catch: Optional[Tuple[Type[BaseException], ...]] = None,
        fallback_value: Any = NOT_SET,
    ) -> None:
        self.max_tries = max(
            num_tries if num_tries is not None else self.default_num_tries, 1
        )
        self._delay = delay if delay is not None else self.default_delay
        self._backoff_generator_func = backoff if backoff is not None else self.backoff
        self._log_level = log_level if log_level is not None else self.default_log_level
        self._exceptions_to_catch = exceptions_to_catch or self.default_exceptions
        self._lazy_logger = logger

        self._fallback_value = fallback_value
        if self._fallback_value is self.NOT_SET:
            self._fallback_value = self.default_fallback_value

        self._backoff_generator = self._backoff_generator_func(self._delay)
        self._tries_remaining = 0
        self._exception: Optional[BaseException] = None

        self.method: Optional[Callable] = None
        self.method_parent = None
        self.method_args: Optional[Tuple] = None
        self.method_kwargs: Optional[Dict[str, Any]] = None
        self._previous_responses: List[Any] = []

    @property
    def _logger(self) -> logging.Logger:
        if self._lazy_logger is None:
            self._lazy_logger = logging.Logger(__name__)

        return self._lazy_logger

    @classmethod
    def doubling_backoff(cls, start: int) -> Generator[int, None, None]:
        """
        Generate delay that doubles with each retry in seconds. If start delay is 0,
        delay of 1 second is used.

        Arguments:
            start -- Starting value of the delay

        Returns:
            A generator of delay in seconds.
        """
        while True:
            start = max(1, start)
            yield start
            start *= 2

    @classmethod
    def no_backoff(cls, start: int) -> Generator[int, None, None]:
        """
        Generate the delay duration between each retry in seconds.
        Always uses `start` delay.

        Arguments:
            start -- Starting value of the delay

        Returns:
            A generator of delay in seconds.
        """
        while True:
            yield start

    @classmethod
    def backoff(cls, start: int) -> Generator[int, None, None]:
        """
        Override this method in a subclass to use a different backoff generator.
        Doubling backoff generator is used.

        Arguments:
            start -- Starting value of the delay

        Returns:
            A generator of delay in seconds.
        """
        return cls.doubling_backoff(start)

    @staticmethod
    def get_exception_scope(exc: BaseException) -> Dict[str, Any]:
        """
        Get original method scope from exception object.

        Arguments:
            exc - Exception object

        Returns:
            A scope as a dict.
        """
        tb = exc.__traceback__
        if tb is None:
            return {}
        tb_next = tb.tb_next
        if tb_next is None:
            return {}
        return tb_next.tb_frame.f_locals

    def handle_exception(
        self, exc: BaseException
    ) -> None:  # pylint: disable=unused-argument
        """
        Override this method in a subclass to do something on each failed try.
        You can access decorated method data from here.

        - `self.method` - Decorated method.
        - `self.method_parent` - Decorated method parent or None if it is a function.
        - `self.method_args` - Arguments for method call.
        - `self.method_kwargs` - Keyword arguments for method call.

        Arguments:
            exc -- Raised exception.
        """
        if isinstance(exc, ClientError):
            error_code = get_nested_item(exc.response, ("Error", "Code"))
            if error_code not in self.retry_error_codes:
                raise exc

        if isinstance(exc, BatchUnprocessedItemsError):
            items_count = len(exc.unprocessed_items)
            message = (
                f"{items_count} unprocessed {pluralize(items_count, 'item')} left."
            )
            self._logger.log(msg=message, level=self._log_level)

            self._previous_responses.append(exc.response)
            if self.method_args is not None:
                self.method_args = (exc.unprocessed_items,) + self.method_args[1:]

    def _handle_exception(self, exc: BaseException) -> None:
        """
        Handle an expected exception

        Arguments:
            exc -- Expected exception
        """
        self.handle_exception(exc=exc)
        self._tries_remaining -= 1

    def _fallback(self) -> Any:
        """
        Fallback when the last retry failed. Return a fallback value if it s set,
        raise expected exception otherwise.

        Returns:
            A fallback value.
        """
        if self._fallback_value is self.NOT_SET:
            if self._exception is not None:
                raise self._exception

        msg = f"Return {self._fallback_value} as a fallback."
        self._log(msg, use_defined_log_level=True)
        return self._fallback_value

    def _log(self, message: str, use_defined_log_level: bool = False) -> None:
        """
        Logs a message with log_level = WARNING if the use_defined_log_level is set to False
        else logs it with defined log_level

        Arguments:
            message - message to be logged
            use_defined_log_level - flag to identify if log should be logged using defined log_level
        """
        log_level = logging.WARNING
        if use_defined_log_level:
            log_level = self._log_level

        self._logger.log(msg=message, level=log_level)
        if self._exception is not None:
            message = f"{self._exception.__class__.__name__}: {self._exception}"
            self._logger.log(msg=message, level=log_level, exc_info=self._exception)

    def __call__(self, f: FunctionType) -> FunctionType:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            self.method = f
            self.method_parent = None
            if args and hasattr(args[0], self.method.__name__):
                self.method_parent = args[0]

            self.method_args = args
            self.method_kwargs = kwargs

            self._tries_remaining = self.max_tries
            self._exception = None
            self._previous_responses.clear()

            while self._tries_remaining > 0:
                try:
                    response = self.method(*self.method_args, **self.method_kwargs)
                    if isinstance(response, dict) and self._previous_responses:
                        response["PreviousResponses"] = self._previous_responses

                    return response

                except self._exceptions_to_catch as e:
                    self._exception = e
                    self._handle_exception(e)

                    # log exception with a traceback and set delay before the next retry.
                    delay = next(self._backoff_generator)
                    message = (
                        f"Backing off for {delay} {pluralize(delay, 'second')} and"
                        f" retrying {self._tries_remaining} more"
                        f" {pluralize(self._tries_remaining, 'time')}."
                    )
                    self._log(message)
                    time.sleep(delay)

            return self._fallback()

        return cast(FunctionType, wrapper)
