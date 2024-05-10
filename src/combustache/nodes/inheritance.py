import textwrap

import combustache.main
from combustache.ctx import MISSING, Ctx
from combustache.nodes.node import Node
from combustache.nodes.section import Section
from combustache.util import Opts, is_whitespace


def pair_if_pair_standalone(first: Node, second: Node) -> None:
    if (
        is_whitespace(first.before)
        and is_whitespace(second.after)
        and first.end == second.start
    ):
        for node in (first, second):
            node.start = node.template.rfind('\n', 0, node.start) + 1
            node.end = node.template.find('\n', node.end) + 1 or len(
                node.template
            )
            node.is_pair_standalone = True


class Block(Section):
    left = '$'

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
        pair_if_pair_standalone(self, self.closing_tag)
        self.init()

    def init(self):
        text = self.template[self.inside_start : self.inside_end]

        # standalone blocks are unique
        # https://github.com/mustache/spec/pull/131#discussion_r668359813
        #    if the end section tag is not standalone by itself, then
        #    the trailing newline will not be removed from the output
        #    if the block ends up being empty
        if (
            not self.closing_tag.is_standalone
            and self.closing_tag.is_pair_standalone
            and not text
        ):
            self.end -= 1
            self.parse_end = self.end

        if self.is_standalone or self.is_pair_standalone:
            dedented_text = textwrap.dedent(text)
            dedented_line = dedented_text.split('\n')[0]
            full_line = text.split('\n')[0]
            self.indent = full_line.removesuffix(dedented_line)

            self.default_value = dedented_text
        else:
            self.default_value = text

    def handle(self, ctx: Ctx, partials: dict[str, str], opts: Opts) -> str:
        data = ctx.inheritance_args.get(self.contents, MISSING)

        if data is MISSING:
            partial_template = self.default_value
        else:
            partial_template = data

        if self.is_standalone or self.is_pair_standalone:
            partial_template = textwrap.indent(
                partial_template, self.indent or self.before
            )
        return combustache.main._render(partial_template, ctx, partials, opts)


class Parent(Section):
    left = '<'

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
        pair_if_pair_standalone(self, self.closing_tag)
        self.parse_end = self.closing_tag.end

        self.blocks = [v for v in self.inside._list if isinstance(v, Block)]

        if self.blocks:
            # {{< parent}}{{$ block}} are pair standalone
            first_block = self.blocks[0]
            pair_if_pair_standalone(self, first_block)
            first_block.inside_start = first_block.end
            # we dont need to set inside_end
            # the only things that change here are parent opening tag and
            # block opening tag, i.e. block closing tag is not affected

            # {{/ parent}}{{/ block}} are pair standalone
            last_block = self.blocks[-1]
            pair_if_pair_standalone(last_block.closing_tag, self.closing_tag)
            self.parse_end = self.closing_tag.end

            # we possibly standaloned these tags
            first_block.init()
            last_block.init()

    def handle(self, ctx: Ctx, partials: dict[str, str], opts: Opts) -> str:
        missing_data = opts['missing_data']

        for block in self.blocks:
            ctx.inheritance_args.setdefault(
                block.contents, block.default_value
            )

        partial_template = partials.get(self.contents)

        if partial_template is None:
            ctx.inheritance_args.clear()
            return missing_data()

        if self.is_standalone or self.is_pair_standalone:
            partial_template = textwrap.indent(partial_template, self.before)

        res = combustache.main._render(partial_template, ctx, partials, opts)
        ctx.inheritance_args.clear()
        return res
