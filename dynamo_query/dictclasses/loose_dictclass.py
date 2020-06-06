from typing import Any, Dict

from dynamo_query.dictclasses.dynamo_dictclass import DynamoDictClass

__all__ = ("LooseDictClass",)


class LooseDictClass(DynamoDictClass):
    """
    DictClass that allows any keys.
    """

    def __init__(self, *args: Dict[str, Any], **kwargs: Any) -> None:
        mappings = [*args, kwargs]
        for mapping in mappings:
            for key in mapping:
                if key not in self._field_names and key not in self._protected_keys:
                    self._field_names.append(key)

        super().__init__(*args, **kwargs)

    def __setitem__(self, key: str, value: Any) -> None:
        if key in self._computers:
            raise KeyError(
                f"{self._class_name}.{key} is computed and cannot be set, got {repr(value)}."
            )

        if key not in self._field_names and key in self._protected_keys:
            self._field_names.append(key)

        self._set_item(key, value, is_initial=False, sanitize_kwargs={})
