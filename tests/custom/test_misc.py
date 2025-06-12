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


def test_not_list_iterables():
    template = '{{#iter}}{{.}}{{/iter}}'
    data = {'iter': (0, 1, 2, 3)}
    expected = '0123'

    out = combustache.render(template, data)
    assert out == expected

    # NOTE: the problem with generators is that they are spent when iterated
    # therefore we cannot guarantee they will work, for example:
    # {{#generator}}{{.}}{{/generator}}{{#generator}}{{.}}{{/generator}}
    #
    # def number_generator():
    #     n = 0
    #     while n < 4:
    #         yield n
    #         n += 1
    #
    # data = {'iter': number_generator()}
    # out = combustache.render(template, data)
    # assert out == expected

    data = {'iter': {0: ')', 1: '!', 2: '@', 3: '#'}.keys()}
    out = combustache.render(template, data)
    assert out == expected

    template = '{{^iter}}empty{{/iter}}'
    data = {'iter': {}.keys()}
    expected = 'empty'

    out = combustache.render(template, data)
    assert out == expected
