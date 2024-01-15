from typing import Any, Callable

import combustache.main
from combustache.ctx import MISSING, Ctx
from combustache.nodes.node import Node
from combustache.util import LAMBDA, is_callable


class Interpolation(Node):
    standalonable = False

    def get_string(
        self,
        data: Any,
        stringify: Callable[[Any], str],
        escape: Callable[[str], str],
    ) -> str:
        return escape(stringify(data))

    def handle(self, ctx: Ctx, partials: dict, opts: dict) -> str:
        stringify = opts['stringify']
        escape = opts['escape']
        missing_data = opts['missing_data']

        data = ctx.get(self.content)
        if data is MISSING:
            return missing_data()

        if is_callable(data):
            if data.__name__ == LAMBDA:
                template = str(data())
                data = combustache.main._render(template, ctx, partials, opts)
            else:
                data = data()

        string = self.get_string(data, stringify, escape)
        return string


class Ampersand(Interpolation):
    left = '&'

    def get_string(
        self,
        data: Any,
        stringify: Callable[[Any], str],
        escape: Callable[[str], str],
    ) -> str:
        return stringify(data)


class Triple(Ampersand):
    left = '{'
    right = '}'
