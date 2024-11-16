from ..ctx import Ctx
from ..util import Opts, is_whitespace


class Node:
    left = ''
    right = ''
    ignorable = False
    standalonable = True

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
        self.contents = contents
        self.template = template
        self.template_start = template_start
        self.template_end = template_end
        self.left_delimiter = left_delimiter
        self.right_delimiter = right_delimiter

        # we +1 to line_start and line_end to get 'hello\n' instad of '\nhello'
        # and we get a nice side effect for end of getting 0 if we dont find \n
        # (i.e. we hit end of string) because str.find returns -1 in that case
        # so we can 'or len(template)' our value to get the end of the template
        line_start = template.rfind('\n', 0, tag_start) + 1
        line_end = template.find('\n', tag_end) + 1 or len(template)

        # string between the last linebreak and node start
        self.before = template[line_start:tag_start]
        # string between node end and the next linebreak
        self.after = template[tag_end:line_end]
        # these are used to check if the tag is standalone

        self.is_pair_standalone = False
        self.is_standalone = is_whitespace(self.before) and is_whitespace(
            self.after
        )
        if self.standalonable and self.is_standalone:
            self.start = line_start
            self.end = line_end
        else:
            self.start = tag_start
            self.end = tag_end
        # parse_end shows the parser from where it should continue parsing
        # tags like Section and Inverted find their closing tag and set
        # parse_end to the end of their closing tag
        self.parse_end = self.end

    @property
    def tag_string(self) -> str:
        return (
            f'{self.left_delimiter}{self.left} '
            f'{self.contents} {self.right}{self.right_delimiter}'
        )

    def handle(self, ctx: Ctx, partials: dict[str, str], opts: Opts) -> str:
        raise NotImplementedError
