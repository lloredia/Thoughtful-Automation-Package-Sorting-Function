"""Command-line interface for the package sorter."""

import argparse
import sys
from collections.abc import Sequence

from package_sorter import __version__
from package_sorter.sorter import sort


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser for the package sorter CLI.

    Returns:
        A parser for width, height, length, and mass.
    """
    parser = argparse.ArgumentParser(
        prog="package_sorter",
        description=(
            "Classify a package as STANDARD, SPECIAL, or REJECTED "
            "from its dimensions (cm) and mass (kg)."
        ),
    )
    parser.add_argument(
        "--width",
        type=float,
        required=True,
        help="Package width in centimeters.",
    )
    parser.add_argument(
        "--height",
        type=float,
        required=True,
        help="Package height in centimeters.",
    )
    parser.add_argument(
        "--length",
        type=float,
        required=True,
        help="Package length in centimeters.",
    )
    parser.add_argument(
        "--mass",
        type=float,
        required=True,
        help="Package mass in kilograms.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Parse arguments, classify the package, and print the stack name.

    Args:
        argv: Arguments to parse. Defaults to the process arguments.

    Returns:
        Process exit code. ``0`` when a stack is printed, ``1`` when the
        measurements are rejected. Argument-parsing errors exit with code 2.
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        stack = sort(args.width, args.height, args.length, args.mass)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(stack)
    return 0
