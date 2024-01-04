class CombustacheError(Exception):
    pass


class DelimiterError(CombustacheError):
    pass


class ClosingTagError(CombustacheError):
    pass
