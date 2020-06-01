from typing import Any, Iterable, List

from dynamo_query.dictclasses.dynamo_dictclass import DynamoDictClass

__all__ = ("LooseDictClass",)


class LooseDictClass(DynamoDictClass):
    """
    DictClass that allows any keys.
    """

    def _get_field_names(self, *mappings: Iterable[str]) -> List[str]:
        result = super()._get_field_names(*mappings)
        for mapping in mappings:
            for key in mapping:
                if key not in result:
                    result.append(key)

        return result

    def __setitem__(self, key: str, value: Any) -> None:
        if key in self._computers:
            raise KeyError(
                f"{self._class_name}.{key} is computed and cannot be set, got {repr(value)}."
            )

        if key not in self._field_names:
            self._field_names.append(key)

        self._set_item(key, value, is_initial=False, sanitize_kwargs={})
