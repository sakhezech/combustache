import html

import combustache.main
from combustache.ctx import Ctx
from combustache.nodes.node import Node
from combustache.util import is_callable, to_str

LAMBDA = '<lambda>'


class Interpolation(Node):
    standalonable = False

    def process_str(self, string: str) -> str:
        return html.escape(to_str(string))

    def handle(self, ctx: Ctx, partials: dict) -> str:
        data = ctx.get(self.content)
        if is_callable(data):
            if data.__name__ == LAMBDA:
                template = str(data())
                data = combustache.main._render(template, ctx, partials)
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
