import pytest

import combustache


def test_left_delimiter_eof():
    template = '{{'
    data = {}

    combustache.render(template, data)


def test_no_content_tag():
    template = '{{}}'
    data = {}

    combustache.render(template, data)


def test_bad_delimiter():
    template = '{{= a a a =}}'
    data = {}

    with pytest.raises(combustache.DelimiterError):
        combustache.render(template, data)


def test_section_not_closed():
    template = '{{#section}} hello'
    data = {}

    with pytest.raises(combustache.MissingClosingTagError):
        combustache.render(template, data)


def test_stray_closing_tag():
    template = '{{/closing}} hello'
    data = {}

    with pytest.raises(combustache.StrayClosingTagError):
        combustache.render(template, data)
