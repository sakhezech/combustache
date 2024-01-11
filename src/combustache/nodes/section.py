import combustache.main
from combustache.ctx import Ctx
from combustache.exceptions import ClosingTagError
from combustache.nodes.node import Node
from combustache.util import (
    LAMBDA,
    is_callable,
)


class Section(Node):
    left = '#'

    def __init__(
        self,
        content: str,
        tag_start: int,
        tag_end: int,
        template: str,
        template_start: int,
        template_end: int,
        left_delimiter: str,
        right_delimiter: str,
    ) -> None:
        super().__init__(
            content,
            tag_start,
            tag_end,
            template,
            template_start,
            template_end,
            left_delimiter,
            right_delimiter,
        )

        depth = 0
        search_start = self.end
        while True:
            node_info = combustache.main.find_node(
                template,
                search_start,
                template_end,
                left_delimiter,
                right_delimiter,
            )
            if node_info is None:
                tag = (
                    f'{self.left_delimiter}{self.left}'
                    '{self.content}{self.right}{self.right_delimiter}'
                )
                raise ClosingTagError(
                    f'No closing tag found for {tag} at {self.start}.'
                )

            content, start, end = node_info
            if (
                content[0] == self.left
                and content.removeprefix(self.left).strip() == self.content
            ):
                depth += 1
            elif (
                content[0] == '/'
                and content.removeprefix('/').strip() == self.content
            ):
                if depth == 0:
                    break
                depth -= 1
            search_start = end

        closing_tag = Closing(
            content,
            start,
            end,
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

    def should_be_rendered(self, item):
        return item

    def handle(self, ctx: Ctx, partials: dict, opts: dict) -> str:
        missing_section = opts['missing_section']

        data = ctx.get(self.content)

        if not self.should_be_rendered(data):
            return missing_section()

        if is_callable(data):
            unprocessed = self.template[self.inside_start : self.inside_end]
            if data.__name__ == LAMBDA:
                template = str(data(unprocessed))
                return combustache.main._render(
                    template,
                    ctx,
                    partials,
                    opts,
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
                    node.handle(ctx, partials, opts)
                    if isinstance(node, Node)
                    else node
                    for node in self.inside
                ]
            )
            ctx.pop()
        return ''.join(stack)


class Inverted(Section):
    left = '^'

    def should_be_rendered(self, item):
        return not item


class Closing(Node):
    left = '/'
    ignorable = True
