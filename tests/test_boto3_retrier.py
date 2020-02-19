from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

from dynamo_query.boto3_retrier import Boto3Retrier, BatchUnprocessedItemsError


class TestBoto3Retrier:
    def test_no_backoff(self):
        generator = Boto3Retrier.no_backoff(5)
        assert next(generator) == 5
        assert next(generator) == 5
        assert next(generator) == 5

        generator = Boto3Retrier.no_backoff(0)
        assert next(generator) == 0
        assert next(generator) == 0
        assert next(generator) == 0

    def test_doubling_backoff(self):
        generator = Boto3Retrier.doubling_backoff(5)
        assert next(generator) == 5
        assert next(generator) == 10
        assert next(generator) == 20

        generator = Boto3Retrier.doubling_backoff(0)
        assert next(generator) == 1
        assert next(generator) == 2
        assert next(generator) == 4

    def test_backoff(self):
        generator = Boto3Retrier.backoff(5)
        assert next(generator) == 5
        assert next(generator) == 10
        assert next(generator) == 20

        generator = Boto3Retrier.backoff(0)
        assert next(generator) == 1
        assert next(generator) == 2
        assert next(generator) == 4

    def test_wrap_function(self):
        decorator = Boto3Retrier(
            exceptions_to_catch=(TypeError,), backoff=Boto3Retrier.no_backoff, delay=0,
        )

        @decorator
        def my_func(data, _test=True):
            return data * 2

        @decorator
        def value_error_func():
            if value_error_func.count < 2:
                value_error_func.count += 1
                raise ValueError("value")

            return "success"

        value_error_func.count = 0

        @decorator
        def type_error_func():
            if type_error_func.count < 2:
                type_error_func.count += 1
                raise TypeError("type")

            return "success"

        type_error_func.count = 0

        assert my_func(2, _test=False) == 4
        assert decorator.method.__name__ == "my_func"
        assert decorator.method_parent is None
        assert decorator.method_args == (2,)
        assert decorator.method_kwargs == dict(_test=False)

        with pytest.raises(ValueError):
            value_error_func()

        assert decorator.method.__name__ == "value_error_func"
        assert decorator.method_parent is None

        assert type_error_func() == "success"
        assert decorator.method.__name__ == "type_error_func"
        assert decorator.method_parent is None

    def test_wrap_method(self):
        decorator = Boto3Retrier(
            exceptions_to_catch=(ValueError,), backoff=Boto3Retrier.no_backoff, delay=0,
        )

        class MyClass:
            def __init__(self):
                self.value_error_count = 0
                self.type_error_count = 0

            @decorator
            def my_method(self, data, _test=True):
                return data * 2

            @decorator
            def value_error_method(self):
                if self.value_error_count < 2:
                    self.value_error_count += 1
                    raise ValueError("value")

                return "success"

            @decorator
            def type_error_method(self):
                if self.type_error_count < 2:
                    self.type_error_count += 1
                    raise TypeError("type")

                return "success"

        my_class = MyClass()
        assert my_class.my_method(2, _test=False) == 4
        assert decorator.method.__name__ == "my_method"
        assert decorator.method_parent == my_class
        assert decorator.method_args == (my_class, 2,)
        assert decorator.method_kwargs == dict(_test=False)

        assert my_class.value_error_method() == "success"
        assert decorator.method.__name__ == "value_error_method"

        with pytest.raises(TypeError):
            my_class.type_error_method()

        assert decorator.method.__name__ == "type_error_method"

    def test_fallback(self):
        decorator = Boto3Retrier(
            exceptions_to_catch=(ValueError,),
            backoff=Boto3Retrier.no_backoff,
            delay=0,
            fallback_value="fallback",
        )

        @decorator
        def my_func():
            return "value"

        @decorator
        def value_error_func():
            raise ValueError("value")

        assert my_func() == "value"
        assert value_error_func() == "fallback"

    def test_no_fallback(self) -> None:
        decorator = Boto3Retrier(
            exceptions_to_catch=(ValueError,), backoff=Boto3Retrier.no_backoff, delay=0,
        )

        @decorator
        def my_func():
            return "value"

        @decorator
        def value_error_func():
            raise ValueError("value")

        assert my_func() == "value"
        with pytest.raises(ValueError):
            value_error_func()

    @staticmethod
    def test_previous_responses() -> None:
        decorator = Boto3Retrier(backoff=Boto3Retrier.no_backoff, delay=0,)

        @decorator
        def value_error_func(items):
            if not items:
                raise BatchUnprocessedItemsError(["test"], "response")

            return {"key": "value"}

        value_error_func.counter = 0

        assert value_error_func(tuple()) == {
            "PreviousResponses": ["response"],
            "key": "value",
        }

    @staticmethod
    def test_get_exception_scope() -> None:
        exc = MagicMock()
        exc.__traceback__ = None
        assert Boto3Retrier.get_exception_scope(exc) == {}
        exc.__traceback__ = MagicMock()
        exc.__traceback__.tb_next = None
        assert Boto3Retrier.get_exception_scope(exc) == {}
        exc.__traceback__.tb_next = MagicMock()
        exc.__traceback__.tb_next.tb_frame.f_locals = {"key": "value"}
        assert Boto3Retrier.get_exception_scope(exc) == {"key": "value"}

    @staticmethod
    def test_handle_exception() -> None:
        decorator = Boto3Retrier(
            backoff=Boto3Retrier.no_backoff, delay=0, fallback_value="fallback",
        )
        exc = ValueError("test")
        assert decorator.handle_exception(exc) is None
        exc = ClientError({"Error": {"Code": "ThrottlingException"}}, "test")
        assert decorator.handle_exception(exc) is None

        exc = ClientError({"Error": {"Code": "UnknownException"}}, "test")
        with pytest.raises(ClientError):
            decorator.handle_exception(exc)

        exc = BatchUnprocessedItemsError(["test"], "response")
        assert str(exc) == "response"
        decorator.handle_exception(exc)
        assert decorator.method_args is None
