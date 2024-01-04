import re
from typing import Any

CONTENT = 'content'
LAMBDA = '<lambda>'


def construct_regex_pattern(
    left_delimiter: str,
    right_delimiter: str,
    left_symbol: str = '',
    right_symbol: str = '[}=]?',
) -> re.Pattern:
    # add note that left and right symbols are not escaped
    left_delimiter = re.escape(left_delimiter)
    right_delimiter = re.escape(right_delimiter)
    return re.compile(
        rf'{left_delimiter}(?P<{CONTENT}>{left_symbol}'
        rf'[\S\s]*?{right_symbol}){right_delimiter}'
    )


def is_whitespace(string: str) -> bool:
    # ''.isspace() returns False
    # for our purposes if there is nothing after or behind the tag
    # it still should count as whitespace and the tag should be standalone
    return not string or string.isspace()


def is_mapping(val) -> bool:
    # isinstance for collections.abc if too slow
    return hasattr(val, '__getitem__') and hasattr(val, 'values')


def is_sequence(val) -> bool:
    # isinstance for collections.abc if too slow
    return hasattr(val, '__getitem__') and hasattr(val, 'index')


def is_callable(val) -> bool:
    # isinstance for collections.abc if too slow
    return hasattr(val, '__call__')


def to_str(val: Any) -> str:
    # basic str(...) but with None accounted
    if val is None:
        return ''
    return str(val)
