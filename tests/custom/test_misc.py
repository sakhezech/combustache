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


def test_cutsom_iterables_in_sections():
    class MyCoolIterable:
        def __init__(self, *args) -> None:
            self.inner = args

        def __iter__(self):
            return self.inner.__iter__()

    my_cool_iterable = MyCoolIterable(1, 2, 3, 4, 5)

    template = '{{#iter}}{{.}}{{/iter}}{{^iter}}nothing here{{/iter}}'
    data = {'iter': my_cool_iterable}
    expected = '12345'

    out = combustache.render(template, data)
    assert out == expected

    # this checks iterables that are not bool(x) is False if they are empty
    my_cool_empty_iterable = MyCoolIterable()

    data = {'iter': my_cool_empty_iterable}
    expected = 'nothing here'

    out = combustache.render(template, data)
    assert out == expected
