import re

from combustache.exceptions import DelimiterError
from combustache.nodes.node import Node


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
