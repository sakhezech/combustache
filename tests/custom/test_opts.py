import combustache
import pytest


def test_stringify():
    template = 'This statement is {{bool}}.'
    data = {'bool': True}
    expected = 'This statement is true.'

    def lowercase_bool(val):
        if val is None:
            return ''
        if isinstance(val, bool):
            return str(val).lower()
        return str(val)

    out = combustache.render(template, data, stringify=lowercase_bool)
    assert out == expected


def test_escape():
    template = 'I am escaping quotes: {{quotes}}'
    data = {'quotes': '" " \' \''}
    expected = r'I am escaping quotes: \" \" \' \''

    def escape_quotes(string: str) -> str:
        return string.replace("'", r'\'').replace('"', r'\"')

    out = combustache.render(template, data, escape=escape_quotes)
    assert out == expected


def test_missing_data():
    template = 'Location: {{location}}.'
    data = {}
    expected = 'Location: UNKNOWN.'

    out = combustache.render(template, data, missing_data=lambda: 'UNKNOWN')
    assert out == expected

    def raise_if_missing():
        raise ValueError('MISSING DATA')

    with pytest.raises(ValueError):
        out = combustache.render(template, data, missing_data=raise_if_missing)

    # None is not missing data
    data = {'location': None}
    expected = 'Location: .'
    out = combustache.render(template, data, missing_data=lambda: 'UNKNOWN')
    assert out == expected


def test_missing_partial():
    template = '{{>cool_partial}}'
    data = {'part_of_partial': 321}
    partials = {}
    expected = '(Partial failed to load!)'

    out = combustache.render(
        template,
        data,
        partials,
        missing_data=lambda: '(Partial failed to load!)',
    )
    assert out == expected


def test_missing_section():
    template = (
        'List of your repos:{{#repos}}\n[{{name}}](url) - {{desc}}{{/repos}}'
    )
    data = {'repos': []}
    expected = 'List of your repos:'
    out = combustache.render(
        template, data, missing_data=lambda: ' you have no repos :('
    )
    assert out == expected
    data = {'repos': None}

    out = combustache.render(
        template, data, missing_data=lambda: ' you have no repos :('
    )
    assert out == expected

    data = {}
    expected = 'List of your repos: you have no repos :('
    out = combustache.render(
        template, data, missing_data=lambda: ' you have no repos :('
    )
    assert out == expected
