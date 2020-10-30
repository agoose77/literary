import importlib.machinery
import os
import pathlib
import linecache
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

    def update_linecache(self, path: str, source: str):
        linecache.cache[path] = (
            len(source),
            None,
            source.splitlines(keepends=True),
            path,
        )

    def get_data(self, path: str):
        c = traitlets.config.Config()
        nb = nbformat.read(path, as_version=nbformat.NO_CONVERT)
        exporter = LiteraryPythonExporter(config=c)
        body, resources = exporter.from_notebook_node(nb)
        # Ensure that generated source is available for tracebacks
        self.update_linecache(path, body)
        return body.encode()


class NotebookFinder(importlib.abc.MetaPathFinder):
    def __init__(self, path):
        self._path = path

    def find_spec(self, fullname, path, target=None):
        if path is None:
            path = self._path
        head, _, module_name = fullname.rpartition(".")

        for entry in path:
            # If we can find {module_name}/__init__.ipynb, this is a package
            package_path = pathlib.Path(entry) / module_name / "__init__.ipynb"
            if package_path.exists():
                spec = importlib.machinery.ModuleSpec(
                    fullname,
                    NotebookLoader(package_path),
                    origin=str(package_path),
                    is_package=True,
                )
                spec.submodule_search_locations = [str(package_path.parent)]
                spec.has_location = True
                return spec

            # Otherwise look for the notebook itself
            module_path = pathlib.Path(entry) / f"{module_name}.ipynb"
            if module_path.exists():
                spec = importlib.machinery.ModuleSpec(
                    fullname, NotebookLoader(module_path), origin=str(module_path)
                )
                spec.has_location = True
                return spec


def install_hook(path=None):
    if path is None:
        path = sys.path
    sys.meta_path.insert(0, NotebookFinder(path))
