from decimal import Decimal
from typing import Any

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
