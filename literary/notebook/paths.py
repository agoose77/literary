import os
import pathlib
from typing import AnyStr, Union

ROOT_PACKAGE_FILES = ["pyproject.toml", "setup.py"]


def find_package_root(path: Union[AnyStr, os.PathLike] = None) -> pathlib.Path:
    """Find the root path of the repository.
    This assumes that all notebooks are imported
    relative to this directory.

    :param path: starting path to traverse from
    :return:
    """
    if path is None:
        path = pathlib.Path.cwd()
    else:
        path = pathlib.Path(path).absolute()

    while path != path.parent:
        for p in ROOT_PACKAGE_FILES:
            if (path / p).exists():
                return path
        path = path.parent
    raise ValueError("Could not find package root")
