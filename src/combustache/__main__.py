import argparse
import json
from pathlib import Path
from typing import Sequence

from combustache.__version__ import __version__
from combustache.main import render
from combustache.util import find_template_files, paths_to_templates


def cli(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser(
        prog='combustache',
        description='an explosive mustache v1.4 implementation with all'
        ' optional modules',
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
        type=Path,
        action='append',
        help='mustache partial file (can add multiple)',
    )

    parser.add_argument(
        '--partial-dir',
        type=Path,
        help='directory with mustache partials',
    )

    parser.add_argument(
        '--partial-ext',
        default='.mustache',
        help="partial file extension (defaults to '.mustache')",
    )

    parser.add_argument(
        '--include-relative-path',
        action='store_true',
        help="include template's relative path in its name"
        ' (defaults to False)',
    )

    parser.add_argument(
        '--left-delimiter',
        default='{{',
        help="left mustache template delimiter (defaults to '{{')",
    )

    parser.add_argument(
        '--right-delimiter',
        default='}}',
        help="right mustache template delimiter (defaults to '}}')",
    )

    args = parser.parse_args(argv)

    if args.string:
        template = args.template
    else:
        with open(args.template) as f:
            template = f.read()

    data = json.load(args.data)

    if args.partial is None:
        args.partial = []

    partials = paths_to_templates(
        args.partial, args.partial_ext, False, Path('.')
    )

    if args.partial_dir:
        partial_files = find_template_files(args.partial_dir, args.partial_ext)
        partials_from_dir = paths_to_templates(
            partial_files,
            args.partial_ext,
            args.include_relative_path,
            args.partial_dir,
        )
        partials.update(partials_from_dir)

    left_delimiter = args.left_delimiter
    right_delimiter = args.right_delimiter

    output = render(template, data, partials, left_delimiter, right_delimiter)
    args.output.write(output)


if __name__ == '__main__':
    cli()
