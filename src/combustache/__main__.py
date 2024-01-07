import argparse
import json
from pathlib import Path
from typing import Sequence

from combustache.__version__ import __version__
from combustache.main import render


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

    parser.add_argument(
        '--partial-dir',
        help='directory with mustache partials',
    )

    parser.add_argument(
        '--partial-pattern',
        default='**/*.mustache',
        help='partial file pattern (defaults to **/*.mustache)',
    )

    parser.add_argument(
        '--left-delimiter',
        default='{{',
        help="left mustache template demimiter (defaults to '{{')",
    )

    parser.add_argument(
        '--right-delimiter',
        default='}}',
        help="right mustache template demimiter (defaults to '}}')",
    )

    args = parser.parse_args(argv)

    if args.string:
        template = args.template
    else:
        with open(args.template) as f:
            template = f.read()

    if args.partial is None:
        args.partial = []

    data = json.load(args.data)

    partials = {}
    for file in args.partial:
        partials.update(json.load(file))
    if args.partial_dir:
        dir_path = Path(args.partial_dir)
        partial_paths = dir_path.rglob(args.partial_pattern)
        for path in partial_paths:
            with path.open() as file:
                partials.update(json.load(file))

    left_delimiter = args.left_delimiter
    right_delimiter = args.right_delimiter

    output = render(template, data, partials, left_delimiter, right_delimiter)
    args.output.write(output)


if __name__ == '__main__':
    cli()
