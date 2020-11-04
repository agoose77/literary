import argparse
import pathlib

from .. import package


def run(argv=None):
    parser = argparse.ArgumentParser(
        description="Build a pure-Python package from a set of Jupyter notebooks"
    )
    parser.add_argument(
        "source", type=pathlib.Path, help="source directory for notebooks"
    )
    parser.add_argument(
        "dest_root", type=pathlib.Path, help="path to parent of generated package"
    )
    args = parser.parse_args(argv)

    package.build_package(args.source, args.dest_root)
