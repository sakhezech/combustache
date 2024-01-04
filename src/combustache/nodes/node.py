import re

from combustache.ctx import Ctx
from combustache.util import CONTENT, is_whitespace


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
