import re

import combustache.main
from combustache.ctx import Ctx
from combustache.exceptions import ClosingTagError
from combustache.nodes.node import Node
from combustache.util import (
    CONTENT,
    LAMBDA,
    construct_regex_pattern,
    is_callable,
)


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
        self.inside = combustache.main.parse(
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
                return combustache.main._render(
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


class Closing(Node):
    left = '/'
    ignorable = True
