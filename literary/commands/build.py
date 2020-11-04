import pathlib

from .. import package


def configure(subparsers):
    parser = subparsers.add_parser(
        "build",
        description="Build a pure-Python package from a set of Jupyter notebooks",
    )
    parser.add_argument(
        "source", type=pathlib.Path, help="source directory for notebooks"
    )
    parser.add_argument(
        "dest_root", type=pathlib.Path, help="path to parent of generated package"
    )
    return parser


def run(args):
    package.build_package(args.source, args.dest_root)
