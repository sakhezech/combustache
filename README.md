# combustache

[![CI](https://github.com/sakhezech/combustache/actions/workflows/ci.yaml/badge.svg)](https://github.com/sakhezech/combustache/actions/workflows/ci.yaml)

Cached Mustache v1.4 implementation with all optional modules.

Usable both in code and as CLI.
To render a mustache template use `combustache.render`.
To clear cache use `combustache.cache_clear`.
To load templates/partials from a directory use `combustache.load_templates`.
To work with template objects directly use `combustache.Template`.

## Installation

From [PyPI](https://pypi.org/project/combustache/):

```sh
pip install combustache
```

From git:

```sh
pip install git+https://github.com/sakhezech/combustache
```

## Usage in code

### Loading templates/partials

```py
>>> # my_project/
>>> # ├─ templates/
>>> # │  ├─ ui/
>>> # │  │  └─ comment.mustache
>>> # │  ├─ index.mustache
>>> # │  └─ other.file
>>> # └─ ...
>>> combustache.load_templates('./templates/', '.mustache')
{
    'comment': "<div class='comment'> {{content}} </div>",
    'index': '<h1> Welcome, {{username}}! </h1>',
}
>>> combustache.load_templates('./templates/', '.mustache',
... include_relative_path=True)
{
    'ui.comment': "<div class='comment'> {{content}} </div>",
    'index': '<h1> Welcome, {{username}}! </h1>',
}
```

### Basic

```py
>>> template = 'Hello {{place}}!'
>>> data = {'place': 'world'}
>>> combustache.render(template, data)
'Hello world!'
```

### Partials

Partials have to be provided as a dictionary.

```py
>>> template = 'My {{>md_link}}!'
>>> data = {'name': 'Github', 'url': 'https://github.com/sakhezech'}
>>> partials = {'md_link': '[{{name}}]({{url}})'}
>>> combustache.render(template, data, partials)
'My [Github](https://github.com/sakhezech)!'
```

### Custom delimiters

You can specify the delimiters outside the template.

```py
>>> template = 'My name is <%name%>.'
>>> data = {'name': 'Anahit'}
>>> combustache.render(template, data, left_delimiter='<%', right_delimiter='%>')
'My name is Anahit.'
```

### Lambda support

```py
>>> template = 'Hello, {{labmda}}!'
>>> data = {'planet': 'world', 'labmda': lambda: '{{planet}}'}
>>> combustache.render(template, data)
'Hello, world!'
```

### Dynamic partials support

```py
>>> template = '{{>*dynamic}}'
>>> data = {'dynamic': 'content'}
>>> partials = {'content': 'something'}
>>> combustache.render(template, data, partials)
'something'
```

### Inheritance support

```py
>>> template = '{{< div}}{{$content}}hello :){{/content}}{{/ div}}'
>>> data = {}
>>> partials = {'div': '<div>{{$content}}default{{/content}}</div>'}
>>> combustache.render(template, data, partials)
'<div>hello :)</div>'
```

### List indexing

You can index into lists by dotting into them with a number.

```py
>>> data = {'items': ['Apricot', 'Cherry', 'Pomegranate']}
>>> template = 'The first item is {{items.0}}.'
>>> combustache.render(template, data)
'The first item is Apricot.'
>>> template = 'The last item is {{items.-1}}.'
>>> combustache.render(template, data)
'The last item is Pomegranate.'
```

### Custom stringify

You can provide a custom stringify function if needed.

Note: `None -> ''` happens here, so you will need to handle this case yourself.

```py
>>> template = 'This statement is {{bool}}.'
>>> data = {'bool': True}
>>> def lowercase_bool(val):
...     if val is None:
...         return ''
...     if isinstance(val, bool):
...         return str(val).lower()
...     return str(val)
...
>>> combustache.render(template, data, stringify=lowercase_bool)
'This statement is true.'
```

### Custom escaping

If you need some other way of escaping your data, you can provide a custom escaping function.

```py
>>> template = 'Escaped: {{content}}; Not escaped: {{{content}}}.'
>>> data = {'content': '{hello}'}
>>> def escape_braces(string):
...     return string.replace('{', r'\{').replace('}', r'\}')
...
>>> combustache.render(template, data, escape=escape_braces)
'Escaped: \\{hello\\}; Not escaped: {hello}.'
```

### Handling missing data

If you want to do something on a missing value, like raise an exception or insert a default value, you can do that too.

Note: `None` is not missing data.

```py
>>> template = '{{something}}'
>>> data = {}
>>> combustache.render(template, data, missing_data=lambda: 'NO DATA')
'NO DATA'
```

## Usage as CLI

`combustache ...` or `python -m combustache ...`

```console
$ combustache -h
usage: combustache [-h] [-v] [-s] [-d DATA] [-o OUTPUT] [-p PARTIAL]
                   [--partial-dir PARTIAL_DIR] [--partial-ext PARTIAL_EXT]
                   [--include-relative-path] [--left-delimiter LEFT_DELIMITER]
                   [--right-delimiter RIGHT_DELIMITER]
                   template

an explosive mustache v1.4 implementation with all optional modules

positional arguments:
  template              mustache template file (use -s for string)

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -s, --string          pass in a string instead of a file for template
  -d DATA, --data DATA  data json file (defaults to stdin)
  -o OUTPUT, --output OUTPUT
                        output file (defaults to stdout)
  -p PARTIAL, --partial PARTIAL
                        mustache partial file (can add multiple)
  --partial-dir PARTIAL_DIR
                        directory with mustache partials
  --partial-ext PARTIAL_EXT
                        partial file extension (defaults to '.mustache')
  --include-relative-path
                        include template's relative path in its name (defaults
                        to False)
  --left-delimiter LEFT_DELIMITER
                        left mustache template delimiter (defaults to '{{')
  --right-delimiter RIGHT_DELIMITER
                        right mustache template delimiter (defaults to '}}')
```

## Development

Use `ruff check --fix .` and `ruff format .` to check and format your code.

To get started:

```sh
git clone https://github.com/sakhezech/combustache
cd combustache
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```
