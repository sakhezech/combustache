import argparse
from typing import Sequence

from combustache.__version__ import __version__


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

    args = parser.parse_args(arglist)
    if args.version:
        print(__version__)


if __name__ == '__main__':
    main()
