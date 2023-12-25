import argparse
import json
from typing import Sequence

from combustache.__version__ import __version__
from combustache.render import render


def main(arglist: Sequence[str] | None = None):
    parser = argparse.ArgumentParser(
        prog='combustache',
        description='explosive mustache v1.3 implementation with lambdas',
    )

    parser.add_argument(
        '-v',
        '--version',
        action='store_true',
        help='print program version and exit',
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

    args = parser.parse_args(arglist)
    if args.version:
        print(__version__)
        return

    if args.string:
        template = args.template + '\n'
    else:
        with open(args.template) as f:
            template = f.read()

    data = json.load(args.data)
    partials = {}

    output = render(template, data, partials)
    args.output.write(output)


if __name__ == '__main__':
    main()
