"""
Mustache v1.3 implementation with lambdas.

Usable both in code and as CLI.
To render a mustache template use `combustache.render`
Processed templates are cached; to clear cache use `combustache.cache_clear`

Typical usage in code: ::

    template = 'Hello my name is {{>fancy_name}}!'
    partials = {'fancy_name': '-> {{name}} <-'}
    data = {'name': 'Anahit'}
    output = combustache.render(template, data, partials)
    print(output)

    Hello my name is -> Anahit <-!

Typical usage as CLI: ::

    $ curl https://end.point/v1/api | combustache template.txt -o out.txt
    $ cat out.txt

    Hello world!
"""
from combustache.render import cache_clear, render

__all__ = ['render', 'cache_clear']
