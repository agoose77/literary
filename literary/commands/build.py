import pathlib

from .. import package
from .. import config


def configure(subparsers):
    project_config = config.load_default_config(config.find_project_path())

    parser = subparsers.add_parser(
        "build",
        description="Build a pure-Python package from a set of Jupyter notebooks",
    )
    parser.add_argument(
        "-s",
        "--source",
        type=pathlib.Path,
        default=project_config["source_path"],
        help="source directory for notebooks",
    )
    parser.add_argument(
        "-p",
        "--package",
        type=pathlib.Path,
        default=project_config["package_path"],
        help="destination path generated package",
    )
    parser.add_argument(
        "-i",
        "--ignore",
        help="glob pattern to ignore during recursion",
        action="append",
    )
    return parser


def run(args):
    if args.source is None:
        raise ValueError(f"Invalid source path {args.source!r}")
    if args.package is None:
        raise ValueError(f"Invalid package path {args.package!r}")

    package.build_package(args.source, args.package, args.ignore)
