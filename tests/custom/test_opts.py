import combustache


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
