import argparse
import json
from typing import Sequence

from combustache.__version__ import __version__
from combustache.render import render


def cli(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser(
        prog='combustache',
        description='explosive mustache v1.3 implementation with lambdas',
    )

    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version=__version__,
    )

    parser.add_argument(
        'template',
        help='mustache template file (use -s for string)',
    )

    parser.add_argument(
        '-s',
        '--string',
        action='store_true',
        help='pass in a string instead of a file for template',
    )

    parser.add_argument(
        '-d',
        '--data',
        type=argparse.FileType(),
        default='-',
        help='data json file (defaults to stdin)',
    )

    parser.add_argument(
        '-o',
        '--output',
        type=argparse.FileType('w'),
        default='-',
        help='output file (defaults to stdout)',
    )

    parser.add_argument(
        '-p',
        '--partial',
        type=argparse.FileType(),
        action='append',
        help='partial file (can add multiple)',
    )

    args = parser.parse_args(argv)

    if args.string:
        template = args.template + '\n'
    else:
        with open(args.template) as f:
            template = f.read()

    if args.partial is None:
        args.partial = []

    data = json.load(args.data)
    partials = {
        key: value
        for file in args.partial
        for key, value in json.load(file).items()
    }

    output = render(template, data, partials)
    args.output.write(output)


if __name__ == '__main__':
    cli()
