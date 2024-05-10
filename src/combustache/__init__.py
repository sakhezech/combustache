"""
Cached Mustache v1.4 implementation with all optional modules.

Usable both in code and as CLI.
To render a mustache template use `combustache.render`.
To clear cache use `combustache.cache_clear`.
To load templates/partials from a directory use `combustache.load_templates`.
To work with template objects directly use `combustache.Template`.

Typical usage in code: ::

    >>> import combustache
    >>> template = 'Hello my name is {{>fancy_name}}!'
    >>> partials = {'fancy_name': '-> {{name}} <-'}
    >>> data = {'name': 'Anahit'}
    >>> combustache.render(template, data, partials)
    'Hello my name is -> Anahit <-!'

Typical usage as CLI: ::

    $ curl https://end.point/v1/api | combustache template.txt -o out.txt
    $ cat out.txt
    Hello world!
"""

from combustache.exceptions import (
    CombustacheError,
    DelimiterError,
    MissingClosingTagError,
    StrayClosingTagError,
)
from combustache.main import Template, cache_clear, render
from combustache.util import load_templates

__all__ = [
    'render',
    'cache_clear',
    'Template',
    'CombustacheError',
    'DelimiterError',
    'MissingClosingTagError',
    'StrayClosingTagError',
    'load_templates',
]
