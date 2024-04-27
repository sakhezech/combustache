import functools
import html
from typing import Any, Callable, Type

from combustache.ctx import Ctx
from combustache.nodes import (
    Ampersand,
    Closing,
    Comment,
    Delimiter,
    Interpolation,
    Inverted,
    Node,
    Partial,
    Section,
    Triple,
)
from combustache.util import Opts, to_str

_nodes: set[type[Node]] = {
    Comment,
    Section,
    Ampersand,
    Inverted,
    Closing,
    Triple,
    Partial,
    Delimiter,
}
_node_types = {node.left: node for node in _nodes}


def find_node(
    template: str,
    search_start: int,
    template_end: int,
    left_delimiter: str,
    right_delimiter: str,
) -> tuple[Type[Node], str, int, int] | None:
    start_idx = template.find(left_delimiter, search_start, template_end)
    if start_idx < search_start:
        return None

    left_idx = start_idx + len(left_delimiter)
    if left_idx >= template_end:
        return None

    node_type = _node_types.get(template[left_idx], Interpolation)
    left = node_type.left
    right = node_type.right

    new_right_delimiter = right + right_delimiter
    right_idx = template.find(new_right_delimiter, left_idx, template_end)
    if right_idx < left_idx:
        return None

    end_idx = right_idx + len(new_right_delimiter)
    content = template[left_idx + len(left) : right_idx].strip()
    return node_type, content, start_idx, end_idx


class Template:
    def __init__(
        self,
        template: str,
        left_delimiter: str = '{{',
        right_delimiter: str = '}}',
        template_start: int = 0,
        template_end: int | None = None,
    ) -> None:
        self._list = self.parse(
            template,
            template_start,
            template_end,
            left_delimiter,
            right_delimiter,
        )

    @staticmethod
    @functools.cache
    def parse(
        template: str,
        template_start: int = 0,
        template_end: int | None = None,
        left_delimiter: str = '{{',
        right_delimiter: str = '}}',
    ) -> list[Node | str]:
        if template_end is None:
            template_end = len(template)
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

            node_type, content, start, end = node_info
            node = node_type(
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

    def _render(self, ctx: Ctx, partials: dict[str, str], opts: Opts) -> str:
        return ''.join(
            node.handle(ctx, partials, opts)
            if isinstance(node, Node)
            else node
            for node in self._list
        )

    def render(
        self,
        data: dict[str, Any],
        partials: dict[str, str] | None = None,
        *,
        stringify: Callable[[Any], str] = to_str,
        escape: Callable[[str], str] = html.escape,
        missing_data: Callable[[], Any] = lambda: '',
    ) -> str:
        opts: Opts = {
            'stringify': stringify,
            'escape': escape,
            'missing_data': missing_data,
        }
        if partials is None:
            partials = {}
        ctx = Ctx([data])
        return self._render(ctx, partials, opts)


def _render(
    template: str,
    ctx: Ctx,
    partials: dict[str, str],
    opts: Opts,
    left_delimiter: str = '{{',
    right_delimiter: str = '}}',
) -> str:
    root = Template(template, left_delimiter, right_delimiter)
    return root._render(ctx, partials, opts)


def render(
    template: str,
    data: dict[str, Any],
    partials: dict[str, str] | None = None,
    left_delimiter: str = '{{',
    right_delimiter: str = '}}',
    *,
    stringify: Callable[[Any], str] = to_str,
    escape: Callable[[str], str] = html.escape,
    missing_data: Callable[[], Any] = lambda: '',
) -> str:
    """
    Renders a mustache template.

    Args:
        template: Mustache template.
        data: Values to insert into the template.
        partials: Partials to insert into the template.
        left_delimiter: Left tag delimiter.
        right_delimiter: Right tag delimiter.

    Keyword args:
        stringify: String conversion function.
        escape: Escaping function.
        missing_data: Function called on missing data.

    Returns:
        Rendered template.

    Raises:
        DelimiterError: Bad delimiter tag.
        MissingClosingTagError: Missing closing tag.
        StrayClosingTagError: Stray closing tag.
    """
    opts: Opts = {
        'stringify': stringify,
        'escape': escape,
        'missing_data': missing_data,
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
    Template.parse.cache_clear()
