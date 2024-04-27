import combustache.main
from combustache.ctx import MISSING, Ctx
from combustache.exceptions import MissingClosingTagError, StrayClosingTagError
from combustache.nodes.node import Node
from combustache.util import LAMBDA, Opts, find_position, is_callable


class Section(Node):
    left = '#'

    def __init__(
        self,
        contents: str,
        tag_start: int,
        tag_end: int,
        template: str,
        template_start: int,
        template_end: int,
        left_delimiter: str,
        right_delimiter: str,
    ) -> None:
        super().__init__(
            contents,
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
                self.template,
                search_start,
                self.template_end,
                self.left_delimiter,
                self.right_delimiter,
            )
            if node_info is None:
                row, col = find_position(self.template, self.start)
                raise MissingClosingTagError(
                    f'No closing tag found: {self.tag_string} at {row}:{col}'
                )

            NodeType, contents, start, end = node_info
            if contents == self.contents:
                if NodeType is self.__class__:
                    depth += 1
                elif NodeType is Closing:
                    if depth == 0:
                        break
                    depth -= 1

            search_start = end

        # not creating a ClosingTag because it raises the stray tag error
        closing_tag = Node(
            contents,
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
        self.inside = combustache.main.Template(
            self.template,
            self.left_delimiter,
            self.right_delimiter,
            self.inside_start,
            self.inside_end,
        )

    def should_be_rendered(self, item):
        return item and item is not MISSING

    def handle(self, ctx: Ctx, partials: dict[str, str], opts: Opts) -> str:
        missing_data = opts['missing_data']

        data = ctx.get(self.contents)

        if not self.should_be_rendered(data):
            if data is MISSING:
                return missing_data()
            return ''

        if is_callable(data):
            unprocessed = self.template[self.inside_start : self.inside_end]
            # if the callable is a lambda we should call it with the string
            # between the tag and its closing tag and render the result
            # in the current context
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
                # otherwise we should get the result with the string passed in
                try:
                    data = data(unprocessed)
                # or just called
                except TypeError:
                    data = data()

        # if data is not a list we put it into one
        # so we can process it easily
        if not isinstance(data, list) or not data:
            data = [data]

        handled = []
        for item in data:
            ctx.append(item)
            handled.append(self.inside._render(ctx, partials, opts))
            ctx.pop()
        return ''.join(handled)


class Inverted(Section):
    left = '^'

    def should_be_rendered(self, item):
        return not item or item is MISSING


class Closing(Node):
    left = '/'
    ignorable = True

    # Section and Inverted find their closing tags themselves
    # so if the parser tries to create a Closing tag that means that the tag
    # was not opened to be closed
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        row, col = find_position(self.template, self.start)
        raise StrayClosingTagError(
            f'Stray closing tag found: {self.tag_string} at {row}:{col}'
        )
