import combustache


def test_multiline_partial_tag_in_partial():
    template = '{{>partial_one}}'
    data = {}
    partials = {
        'partial_one': '{{>\n       partial_two       \n             }}',
        'partial_two': 'hi',
    }
    expected = 'hi'

    out = combustache.render(template, data, partials)
    assert out == expected
