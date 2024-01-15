from collections.abc import Sequence
from typing import Any

from combustache.util import is_callable, is_mapping, is_sequence

MISSING = object()


class Ctx(list):
    def get(self, key: str) -> Any:
        if key == '.':
            return self[-1]

        chain = key.split('.')
        reverse = reversed(self)
        found = MISSING
        for item in reverse:
            found = get_inside(item, chain[0])
            if found is not MISSING:
                break

        if found is MISSING:
            return MISSING

        for key in chain[1:]:
            found = get_inside(found, key)
        return found


def sequence_get(seq: Sequence, index: int) -> Any:
    try:
        return seq[index]
    except IndexError:
        return MISSING


def to_int(string: str) -> int | None:
    try:
        return int(string)
    except ValueError:
        return None


def get_inside(item: Any, key: str) -> Any | None:
    if is_callable(item):
        item = item()

    if is_mapping(item):
        return item.get(key, MISSING)
    elif is_sequence(item) and (num := to_int(key)) is not None:
        return sequence_get(item, num)
    else:
        return getattr(item, key, MISSING)
