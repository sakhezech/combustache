import functools
import html
from typing import Any, Callable

from combustache.ctx import Ctx
from combustache.nodes.comment import Comment
from combustache.nodes.delimiter import Delimiter
from combustache.nodes.interpolation import Ampersand, Interpolation, Triple
from combustache.nodes.node import Node
from combustache.nodes.partial import Partial
from combustache.nodes.section import Inverted, Section  # , Closing
from combustache.util import to_str


def create_node(
    content: str,
    tag_start: int,
    tag_end: int,
    template: str,
    template_start: int,
    template_end: int,
    left_delimiter: str,
    right_delimiter: str,
) -> Node:
    kwargs = {
        'content': content,
        'tag_start': tag_start,
        'tag_end': tag_end,
        'template': template,
        'template_start': template_start,
        'template_end': template_end,
        'left_delimiter': left_delimiter,
        'right_delimiter': right_delimiter,
    }
    if not content:
        content = ' '
    first_char, last_char = content[0], content[-1]
    match (first_char, last_char):
        case ('!', _):
            return Comment(**kwargs)
        case ('#', _):
            return Section(**kwargs)
        case ('&', _):
            return Ampersand(**kwargs)
        case ('{', '}'):
            return Triple(**kwargs)
        case ('=', '='):
            return Delimiter(**kwargs)
        case ('^', _):
            return Inverted(**kwargs)
        case ('>', _):
            return Partial(**kwargs)
        case (_, _):
            return Interpolation(**kwargs)


def find_node(
    template: str,
    search_start: int,
    template_end: int,
    left_delimiter: str,
    right_delimiter: str,
) -> tuple[str, int, int] | None:
    start_idx = template.find(left_delimiter, search_start, template_end)
    if start_idx < search_start:
        return None

    left_idx = start_idx + len(left_delimiter)
    if left_idx >= template_end:
        return None

    if template[left_idx] == '{':
        new_delimiter = '}' + right_delimiter
        to_add = 1
    elif template[left_idx] == '=':
        new_delimiter = '=' + right_delimiter
        to_add = 1
    else:
        new_delimiter = right_delimiter
        to_add = 0

    right_idx = template.find(new_delimiter, left_idx, template_end)
    if right_idx < left_idx:
        return None

    end_idx = right_idx + len(new_delimiter)
    content = template[left_idx : right_idx + to_add]
    return content, start_idx, end_idx


@functools.cache
def parse(
    template: str,
    template_start: int,
    template_end: int,
    left_delimiter: str = '{{',
    right_delimiter: str = '}}',
) -> list[Node | str]:
    nodes = []
    search_start = template_start
    while True:
        node_info = find_node(
            template,
            search_start,
            template_end,
            left_delimiter,
            right_delimiter,
        )

        if node_info is None:
            nodes.append(template[search_start:template_end])
            break

        content, start, end = node_info
        node = create_node(
            content,
            start,
            end,
            template,
            template_start,
            template_end,
            left_delimiter,
            right_delimiter,
        )

        if isinstance(node, Delimiter):
            left_delimiter = node.left_delimiter
            right_delimiter = node.right_delimiter

        nodes.append(template[search_start : node.start])
        if not node.ignorable:
            nodes.append(node)
        search_start = node.parse_end
    return nodes


def _render(
    template: str,
    ctx: Ctx,
    partials: dict,
    opts: dict,
    left_delimiter: str = '{{',
    right_delimiter: str = '}}',
) -> str:
    root = parse(template, 0, len(template), left_delimiter, right_delimiter)
    return ''.join(
        [
            node.handle(ctx, partials, opts)
            if isinstance(node, Node)
            else node
            for node in root
        ]
    )


def render(
    template: str,
    data: dict,
    partials: dict | None = None,
    left_delimiter: str = '{{',
    right_delimiter: str = '}}',
    *,
    stringify: Callable[[Any], str] = to_str,
    escape: Callable[[str], str] = html.escape,
    missing_data: Callable = lambda: '',
    missing_partial: Callable = lambda: '',
    missing_section: Callable = lambda: '',
) -> str:
    """
    Renders a mustache template.

    Args:
        template (str): Mustache template.
        data (dict): Values to insert into the template.
        partials (dict): Partials to use while rendering.
        left_delimiter (str): Left tag delimiter.
        right_delimiter (str): Right tag delimiter.

    Returns:
        str: Rendered template.

    Raises:
        DelimiterError: Bad delimiter tag.
        ClosingTagError: No closing tag.
    """
    opts = {
        'stringify': stringify,
        'escape': escape,
        'missing_data': missing_data,
        'missing_partial': missing_partial,
        'missing_section': missing_section,
    }
    if partials is None:
        partials = {}
    ctx = Ctx([data])
    return _render(
        template, ctx, partials, opts, left_delimiter, right_delimiter
    )


def cache_clear():
    """
    Clears cached templates.
    """
    parse.cache_clear()
