class CombustacheError(Exception):
    pass


class DelimiterError(CombustacheError):
    pass


class MissingClosingTagError(CombustacheError):
    pass


class StrayClosingTagError(CombustacheError):
    pass
