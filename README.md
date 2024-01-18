# combustache

Mustache v1.3 implementation with lambdas.

Usable both in code and as CLI.
To render a mustache template use `combustache.render`.
Processed templates are cached; to clear cache use `combustache.cache_clear`.

## Installation

From [PyPI](https://pypi.org/project/combustache/):

```sh
pip install combustache
```

From git:

```sh
pip install git+https://github.com/sakhezech/combustache
```

## Usage

### Typical usage in code

```py
>>> import combustache
>>> template = 'Hello my name is {{>fancy_name}}!'
>>> partials = {'fancy_name': '-> {{name}} <-'}
>>> data = {'name': 'Anahit'}
>>> combustache.render(template, data, partials)
'Hello my name is -> Anahit <-!'
```

### Typical usage as CLI

`combustache ...` or `python -m combustache ...`

For more info use `combustache -h`.

```sh
$ curl https://end.point/v1/api | combustache template.txt -o out.txt
$ cat out.txt
Hello world!
```
