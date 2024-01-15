import combustache.main
from combustache.ctx import Ctx
from combustache.nodes.node import Node


class Partial(Node):
    left = '>'

    def handle(self, ctx: Ctx, partials: dict, opts: dict) -> str:
        missing_data = opts['missing_data']

        partial_template = partials.get(self.content)

        if partial_template is None:
            return missing_data()

        partial_lines = partial_template.split('\n')
        if self.is_standalone:
            stack = [
                bool(line) * self.before
                + combustache.main._render(line, ctx, partials, opts)
                for line in partial_lines
            ]
        else:
            stack = [
                combustache.main._render(line, ctx, partials, opts)
                for line in partial_lines
            ]
        return '\n'.join(stack)
