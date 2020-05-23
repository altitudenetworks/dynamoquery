import string
from typing import Any, Dict, Iterable, Iterator, List, Optional, Set


def chunkify(data: Iterable, size: int) -> Iterator[List[Any]]:
    """
    Splits data to chunks of `size` length or less.

    ```python
    data = [1, 2, 3, 4, 5]
    for chunk in chunkify(data, size=2):
        print(chunk)

    # [1, 2]
    # [3, 4]
    # [5]
    ```

    Arguments:
        data -- Data to chunkify
        size -- Max chunk size.

    Returns:
        A generator of chunks.
    """
    chunk: List[Any] = []
    for item in data:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []

    if chunk:
        yield chunk


def ascii_string_generator(length: int = 3) -> Iterator[str]:
    """
    Generator to build unique strings from "aa...a" to "zz...z".

    ```python
    gen = ascii_string_generator()
    next(gen)  # 'aaa'
    next(gen)  # 'aab'
    list(gen)[-1]  # 'zzz'
    ```

    Arguments:
        length -- Length of a result string.

    Yields:
        Lowercased ASCII string like "aaa"
    """
    counter = 0
    letters = string.ascii_lowercase
    letters_length = len(letters)
    max_counter = letters_length ** length
    while counter < max_counter:
        result = []
        for pos in range(length - 1, -1, -1):
            letter_index = counter // (letters_length ** pos) % letters_length
            result.append(letters[letter_index])
        counter += 1
        yield "".join(result)


def get_format_keys(format_string: str) -> Set[str]:
    """
    Extract format keys from a formet-ready string.

    ```python
    keys = get_format_keys('key: {key} {value}')
    keys # ['key', 'value']
    ```

    Arguments:
        format_string -- A format-ready string.

    Returns:
        A set of format keys.
    """
    result = set()
    formatter = string.Formatter()
    for _, key, _, _ in formatter.parse(format_string):
        if key:
            result.add(key)

    return result


def pluralize(count: int, singular: str, plural: Optional[str] = None) -> str:
    """
    Pluralize a noun according to `count`.

    Arguments:
        count -- Count of objects.
        singular -- Singular noun form.
        plural -- Plural noun form. If not provided - append `s` to singular form.

    Returns:
        A noun in proper form.
    """
    if count % 10 == 1:
        return singular

    if plural is not None:
        return plural

    return f"{singular}s"


def get_nested_item(
    dict_obj: Dict[str, Any], item_path: Iterable[str], raise_errors: bool = False
) -> Any:
    """
    Get nested `item_path` from `dict_obj`.

    Arguments:
        dict_obj -- Source dictionary.
        item_path -- Keys list.
        raise_errors -- Whether to raise `AttributeError` on not a dictionary item.

    Raises:
        AttributeError -- If nested item is not a dictionary.
    """
    result: Any = dict_obj
    for attr in item_path:
        if not isinstance(result, dict):
            message = f"Cannot get nested path {'/'.join(item_path)}, {result} is not a dictionary"
            if raise_errors:
                raise AttributeError(message)

            return None

        result = result.get(attr)
    return result
