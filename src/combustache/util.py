from os import PathLike
from pathlib import Path
from typing import Any, Callable, TypedDict

StrPath = PathLike[str] | str

LAMBDA = '<lambda>'


class Opts(TypedDict):
    """
    `render` and `Template.render` options.
    """

    stringify: Callable[[Any], str]
    escape: Callable[[str], str]
    missing_data: Callable[[], Any]


def is_whitespace(string: str) -> bool:
    """
    Checks if a string is whitespace.
    """
    # ''.isspace() returns False
    # for our purposes if there is nothing after or behind the tag
    # it still should count as whitespace and the tag should be standalone
    return not string or string.isspace()


def is_callable(val: Any) -> bool:
    return hasattr(val, '__call__')


def to_str(val: Any) -> str:
    """
    Turns a value into a string with None -> ''.

    Args:
        val: Value to stringify.

    Returns:
        Stringified value.
    """
    if val is None:
        return ''
    return str(val)


def find_position(template: str, index: int) -> tuple[int, int]:
    """
    Finds row and column of an index in a template.

    Args:
        template: Template.
        index: Index.

    Returns a tuple (row, col) where:
        row: Row number.
        col: Column number.
    """
    row = template.count('\n', 0, index)
    last_break = template.rfind('\n', 0, index)
    col = index - (last_break + 1)
    return row + 1, col + 1


def find_partial_files(path: Path, extension: str) -> list[Path]:
    return [Path(path) for path in path.rglob(f'**/*{extension}')]


def paths_to_partials(
    partial_paths: list[Path], extension: str
) -> dict[str, str]:
    return {
        path.name.removesuffix(extension): path.read_text()
        for path in partial_paths
    }


def load_partials(path: StrPath, extension: str) -> dict[str, str]:
    """
    Loads partials from a directory.

    Args:
        path: Root directory path.
        extension: Partial file extension.

    Returns:
        Dictionary of partials.
    """
    path = Path(path)
    partial_paths = find_partial_files(path, extension)
    return paths_to_partials(partial_paths, extension)
