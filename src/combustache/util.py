from typing import Any, Callable, TypedDict

LAMBDA = '<lambda>'


class Opts(TypedDict):
    stringify: Callable[[Any], str]
    escape: Callable[[str], str]
    missing_data: Callable[[], Any]


def is_whitespace(string: str) -> bool:
    # ''.isspace() returns False
    # for our purposes if there is nothing after or behind the tag
    # it still should count as whitespace and the tag should be standalone
    return not string or string.isspace()


def is_callable(val) -> bool:
    # isinstance for collections.abc if too slow
    return hasattr(val, '__call__')


def to_str(val: Any) -> str:
    # basic str(...) but with None accounted
    if val is None:
        return ''
    return str(val)


def find_position(template: str, index: int) -> tuple[int, int]:
    row = template.count('\n', 0, index)
    last_break = template.rfind('\n', 0, index)
    col = index - last_break - 1
    return row + 1, col + 1
