"""
Sentinel value than can be used as a placeholder.
"""


class SentinelValue:
    """
    Sentinel value than can be used as a placeholder.
    Doc generation friendly.

    ```python

    NOT_SET = SentinelValue('NOT_SET')

    def check_value(name=NOT_SET):
        if name is NOT_SET:
            return 'This is a NOT_SET value'

        return 'This is something else'

    repr(NOT_SET) # 'NOT_SET'
    ```

    Arguments:
        name -- String used as a representation of the object.
    """

    def __init__(self, name: str = "DEFAULT") -> None:
        self._name = name

    def __repr__(self) -> str:
        return self._name

    def __str__(self) -> str:
        return self._name
