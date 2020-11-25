import importlib.machinery
import linecache
import os
import pathlib
import sys
from typing import AnyStr, Union

import nbformat
import traitlets.config

from ..exporter import LiteraryPythonExporter


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


def determine_package_name(path: pathlib.Path, package_root_path: pathlib.Path) -> str:
    """Determine the corresponding importable name for a package directory given by
    a particular file path

    :param path: path to package
    :param package_root_path: root path containing notebook package directory
    :return:
    """
    relative_path = path.relative_to(package_root_path)
    return ".".join(relative_path.parts)


def install_hook(package_root_path: Union[AnyStr, os.PathLike]):
    """Install notebook import hook

    Don't allow the user to specify a custom search path, because we also need this to
    interoperate with the default Python module importers which use sys.path

    :param package_root_path: root path containing notebook package directory
    :return:
    """
    # Make notebook packages importable by adding package root path to sys.path
    sys.path.append(str(package_root_path))
    sys.meta_path.insert(0, NotebookFinder(sys.path))
