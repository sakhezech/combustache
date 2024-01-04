import functools
import html
import re

from combustache.ctx import Ctx
from combustache.util import (
    CONTENT,
    construct_regex_pattern,
    is_callable,
    is_whitespace,
    to_str,
)

LAMBDA = '<lambda>'


class Node:
    left = ''
    right = ''
    ignorable = False
    standalonable = True

    def __init__(
        self,
        match: re.Match,
        template: str,
        start: int,
        end: int,
        left_delimiter: str,
        right_delimiter: str,
    ) -> None:
        self.template = template
        self.template_start = start
        self.template_end = end
        self.left_delimiter = left_delimiter
        self.right_delimiter = right_delimiter
        self.inside: list[str | Node] = []

        tag_start = match.start()
        tag_end = match.end()

        # we +1 to line_start and line_end to get 'hello\n' instad of '\nhello'
        # and we get a nice side effect for end of getting 0 if we dont find \n
        # (i.e. we hit end of string) because str.find returns -1 in that case
        # so we can 'or len(template)' our value to get the end of the template
        line_start = template.rfind('\n', 0, tag_start) + 1
        line_end = template.find('\n', tag_end) + 1 or len(template)

        self.before = template[line_start:tag_start]
        self.after = template[tag_end:line_end]

        self.is_standalone = is_whitespace(self.before) and is_whitespace(
            self.after
        )
        if self.standalonable and self.is_standalone:
            self.start = line_start
            self.end = line_end
        else:
            self.start = tag_start
            self.end = tag_end
        self.parse_end = self.end

        self.content = (
            match.group(CONTENT)
            .removeprefix(self.left)
            .removesuffix(self.right)
            .strip()
        )

    def handle(self, ctx: Ctx, partials: dict) -> str:
        raise NotImplementedError


class Interpolation(Node):
    standalonable = False

    def process_str(self, string: str) -> str:
        return html.escape(to_str(string))

    def handle(self, ctx: Ctx, partials: dict) -> str:
        data = ctx.get(self.content)
        if is_callable(data):
            if data.__name__ == LAMBDA:
                template = str(data())
                data = _render(template, ctx, partials)
            else:
                data = data()

        string = self.process_str(data)
        return string


class Ampersand(Interpolation):
    left = '&'

    def process_str(self, string: str) -> str:
        return to_str(string)


class Triple(Ampersand):
    left = '{'
    right = '}'


class Section(Node):
    left = '#'

    def __init__(
        self,
        match: re.Match,
        template: str,
        start: int,
        end: int,
        left_delimiter: str,
        right_delimiter: str,
    ) -> None:
        super().__init__(
            match, template, start, end, left_delimiter, right_delimiter
        )
        pattern = construct_regex_pattern(
            self.left_delimiter,
            self.right_delimiter,
            f'[{re.escape(self.left)}/]',
            '',
        )

        i = 0
        found = None
        for match in pattern.finditer(
            self.template, self.end, self.template_end
        ):
            if match.group(CONTENT)[0] == self.left:
                i += 1
            else:
                if i == 0:
                    found = match
                    break
                i -= 1
        if found is None:
            raise ClosingTagError(
                f'No closing tag found for {self.content} at {self.start}'
            )

        closing_tag = Closing(
            found,
            self.template,
            self.template_start,
            self.template_end,
            self.left_delimiter,
            self.right_delimiter,
        )

        self.inside_start = self.end
        self.inside_end = closing_tag.start
        self.parse_end = closing_tag.end
        self.inside = parse(
            self.template,
            self.inside_start,
            self.inside_end,
            self.left_delimiter,
            self.right_delimiter,
        )

    def should_not_be_rendered(self, item):
        return not item

    def handle(self, ctx: Ctx, partials: dict) -> str:
        data = ctx.get(self.content)

        if self.should_not_be_rendered(data):
            return ''

        if is_callable(data):
            unprocessed = self.template[self.inside_start : self.inside_end]
            if data.__name__ == LAMBDA:
                template = str(data(unprocessed))
                return _render(
                    template,
                    ctx,
                    partials,
                    self.left_delimiter,
                    self.right_delimiter,
                )
            else:
                try:
                    data = data(unprocessed)
                except TypeError:
                    data = data()

        if not isinstance(data, list) or not data:
            data = [data]

        stack = []
        for d in data:
            ctx.append(d)
            stack.extend(
                [
                    i if isinstance(i, str) else i.handle(ctx, partials)
                    for i in self.inside
                ]
            )
            ctx.pop()
        return ''.join(stack)


class Inverted(Section):
    left = '^'

    def should_not_be_rendered(self, item):
        return item


class Delimiter(Node):
    left = '='
    right = '='
    ignorable = True

    def __init__(
        self,
        match: re.Match,
        template: str,
        start: int,
        end: int,
        left_delimiter: str,
        right_delimiter: str,
    ) -> None:
        super().__init__(
            match, template, start, end, left_delimiter, right_delimiter
        )
        split = self.content.split()
        if len(split) > 2:
            raise DelimiterError(f'Impossible delimiter tag at {self.start}.')
        self.left_delimiter = split[0]
        self.right_delimiter = split[1]


class Partial(Node):
    left = '>'

    def handle(self, ctx: Ctx, partials: dict) -> str:
        partial_template = partials.get(self.content)
        if partial_template is None:
            return ''
        partial_lines = partial_template.split('\n')
        if self.is_standalone:
            stack = [
                bool(line) * self.before + _render(line, ctx, partials)
                for line in partial_lines
            ]
        else:
            stack = [_render(line, ctx, partials) for line in partial_lines]
        return '\n'.join(stack)


class Comment(Node):
    left = '!'
    ignorable = True


class Closing(Node):
    left = '/'
    ignorable = True


def create_node(
    match: re.Match,
    template: str,
    start: int,
    end: int,
    left_delimiter: str,
    right_delimiter: str,
) -> Node:
    content = match.group(CONTENT)
    first_char, last_char = content[0], content[-1]
    kwargs = {
        'match': match,
        'template': template,
        'start': start,
        'end': end,
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


class CombustacheError(Exception):
    pass


class DelimiterError(CombustacheError):
    pass


class ClosingTagError(CombustacheError):
    pass


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

        node = create_node(
            match,
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
    left_delimiter: str = '{{',
    right_delimiter: str = '}}',
) -> str:
    root = parse(template, 0, len(template), left_delimiter, right_delimiter)
    return ''.join(
        [
            piece.handle(ctx, partials) if isinstance(piece, Node) else piece
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
        partials (dict | None): Partials to use while rendering.
        left_delimiter (str): Left tag delimiter.
        right_delimiter (str): Right tag delimiter.

    Returns:
        str: Rendered template.

    Raises:
        DelimiterError: Bad delimiter tag.
        ClosingTagError: No closing tag.
    """
    if partials is None:
        partials = {}
    ctx = Ctx([data])
    return _render(template, ctx, partials, left_delimiter, right_delimiter)


def cache_clear():
    """
    Clears cached templates.
    """
    parse.cache_clear()
