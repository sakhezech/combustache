import functools

from combustache.ctx import Ctx
from combustache.nodes.comment import Comment
from combustache.nodes.delimiter import Delimiter
from combustache.nodes.interpolation import Ampersand, Interpolation, Triple
from combustache.nodes.node import Node
from combustache.nodes.partial import Partial
from combustache.nodes.section import Inverted, Section  # , Closing
from combustache.util import CONTENT, construct_regex_pattern


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
    first_char, last_char = content[0], content[-1]
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


@functools.cache
def parse(
    template: str,
    template_start: int,
    template_end: int,
    left_delimiter: str = '{{',
    right_delimiter: str = '}}',
) -> list[Node | str]:
    res = []

    pattern = construct_regex_pattern(left_delimiter, right_delimiter)
    start = template_start
    end = template_end

    while True:
        match = pattern.search(template, start, end)
        if match is None:
            res.append(template[start:end])
            break

        tag_start = match.start()
        tag_end = match.end()
        content = match.group(CONTENT)
        node = create_node(
            content,
            tag_start,
            tag_end,
            template,
            template_start,
            template_end,
            left_delimiter,
            right_delimiter,
        )

        # make this better?
        if isinstance(node, Delimiter):
            left_delimiter = node.left_delimiter
            right_delimiter = node.right_delimiter
            pattern = construct_regex_pattern(left_delimiter, right_delimiter)

        res.append(template[start : node.start])
        if not node.ignorable:
            res.append(node)
        start = node.parse_end
    return res


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
            piece.handle(ctx, partials, opts)
            if isinstance(piece, Node)
            else piece
            for piece in root
        ]
    )


def render(
    template: str,
    data: dict,
    partials: dict | None = None,
    left_delimiter: str = '{{',
    right_delimiter: str = '}}',
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
    opts = {}
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
