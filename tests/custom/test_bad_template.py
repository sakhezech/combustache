import combustache


def test_left_delimiter_eof():
    template = '{{'
    data = {}

    combustache.render(template, data)


def test_no_content_tag():
    template = '{{}}'
    data = {}

    combustache.render(template, data)
