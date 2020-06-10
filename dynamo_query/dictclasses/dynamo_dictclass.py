from decimal import Decimal
from typing import Any, List

from dynamo_query.dictclasses.dictclass import DictClass


class DynamoDictClass(DictClass):
    NOT_SET = None

    def _sanitize_key(self, key: str, value: Any, **kwargs: Any) -> Any:
        sanitized_value = super()._sanitize_key(key, value, **kwargs)
        allowed_types = self._allowed_types.get(key)
        if allowed_types and isinstance(sanitized_value, Decimal):
            if float in allowed_types:
                return float(sanitized_value)
            if int in allowed_types:
                return int(sanitized_value)

        return sanitized_value

    @classmethod
    def get_required_field_names(cls) -> List[str]:
        """
        Get a list of required field names.

        Returns:
            A list of field names as strings.
        """
        cls._initalize_class()
        return cls._required_field_names

    @classmethod
    def get_field_names(cls) -> List[str]:
        """
        Get a list of accepted field names.

        Returns:
            A list of field names as strings.
        """
        cls._initalize_class()
        return cls._field_names
