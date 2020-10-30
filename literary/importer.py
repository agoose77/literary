import importlib.machinery
import os
import pathlib
import sys
from typing import AnyStr, Union

import nbformat
import traitlets.config

from .exporter import LiteraryPythonExporter

ROOT_PACKAGE_FILES = ["pyproject.toml", "setup.py"]


def find_package_root(path: Union[AnyStr, os.PathLike]) -> pathlib.Path:
    """Find the root path of the repository.
    This assumes that all notebooks are imported
    relative to this directory.

    :param path:
    :return:
    """
    path = pathlib.Path(path).absolute()

    while path != path.parent:
        for p in ROOT_PACKAGE_FILES:
            if (path / p).exists():
                return path
        path = path.parent
    raise ValueError("Could not find package root")


class NotebookLoader(importlib.abc.SourceLoader):
    def __init__(self, path):
        self.path = path

    def get_filename(self, full_name):
        return str(self.path)

    def get_data(self, path):
        c = traitlets.config.Config()
        nb = nbformat.read(path, as_version=nbformat.NO_CONVERT)
        exporter = LiteraryPythonExporter(config=c)
        body, resources = exporter.from_notebook_node(nb)
        return body.encode()


class NotebookFinder(importlib.abc.MetaPathFinder):
    def __init__(self, path):
        self._path = path

    def find_spec(self, fullname, path, target=None):
        if path is None:
            path = self._path

        head, _, module_name = fullname.rpartition(".")

        for entry in path:
            notebook_path = pathlib.Path(entry) / f"{module_name}.ipynb"
            if notebook_path.exists():
                spec = importlib.machinery.ModuleSpec(
                    fullname, NotebookLoader(notebook_path), origin=str(notebook_path)
                )
                spec.has_location = True
                # spec.parent =
                return spec


def install_hook(path=None):
    if path is None:
        path = sys.path
    sys.meta_path.append(NotebookFinder(path))
