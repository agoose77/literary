import importlib.machinery
import linecache
import traceback
import os
import pathlib
import sys
from typing import AnyStr, Union

import nbformat
import traitlets.config

from ..exporter import LiteraryPythonExporter


class NotebookLoader(importlib.machinery.SourcelessFileLoader):

    def __init__(self, fullname: str, path: str, config):
        super().__init__(fullname, path)

        self.config = config

    def _update_linecache(self, path: str, source: str):
        linecache.cache[path] = (
            len(source),
            None,
            source.splitlines(keepends=True),
            path,
        )

    def get_code(self, fullname: str):
        path = self.get_filename(fullname)
        body = self.get_transpiled_source(path)
        # Ensure that generated source is available for tracebacks
        self._update_linecache(path, body)
        return compile(body, path, 'exec')

    def get_transpiled_source(self, path: str):
        nb = nbformat.read(path, as_version=nbformat.NO_CONVERT)
        exporter = LiteraryPythonExporter(config=self.config)
        body, resources = exporter.from_notebook_node(nb)
        return body


class NotebookFinder(importlib.abc.MetaPathFinder):
    def __init__(self, path, config):
        self._path = path
        self._config = config

    def _load_package_spec(self, path: pathlib.Path,
                           name: str) -> importlib.machinery.ModuleSpec:
        spec = importlib.machinery.ModuleSpec(
            name,
            NotebookLoader(name, str(path), self._config),
            origin=str(path),
            is_package=True,
        )
        spec.submodule_search_locations = [str(path.parent)]
        spec.has_location = True
        return spec

    def _load_module_spec(self, path: pathlib.Path,
                          name: str) -> importlib.machinery.ModuleSpec:
        spec = importlib.machinery.ModuleSpec(
            name, NotebookLoader(name, str(path), self._config), origin=str(path)
        )
        spec.has_location = True
        return spec

    def find_spec(self, fullname, path, target=None):
        if path is None:
            path = self._path
        head, _, module_name = fullname.rpartition(".")

        for entry in path:
            # If we can find {module_name}/__init__.ipynb, this is a package
            package_path = pathlib.Path(entry) / module_name / "__init__.ipynb"
            if package_path.exists():
                return self._load_package_spec(package_path, fullname)

            # Otherwise look for the notebook itself
            module_path = pathlib.Path(entry) / f"{module_name}.ipynb"
            if module_path.exists():
                return self._load_module_spec(module_path, fullname)


def determine_package_name(path: pathlib.Path, package_root_path: pathlib.Path) -> str:
    """Determine the corresponding importable name for a package directory given by
    a particular file path

    :param path: path to package
    :param package_root_path: root path containing notebook package directory
    :return:
    """
    relative_path = path.relative_to(package_root_path)
    return ".".join(relative_path.parts)


def install_hook(
        package_root_path: Union[AnyStr, os.PathLike], set_except_hook: bool = True
):
    """Install notebook import hook

    Don't allow the user to specify a custom search path, because we also need this to
    interoperate with the default Python module importers which use sys.path

    :param package_root_path: root path containing notebook package directory
    :param set_except_hook: overwrite `sys.excepthook` to correctly display tracebacks
    inside notebooks
    :return:
    """
    # Make notebook packages importable by adding package root path to sys.path
    sys.path.append(str(package_root_path))
    sys.meta_path.insert(0, NotebookFinder(sys.path, config=traitlets.config.Config()))

    # Python's C-level traceback reporting doesn't call `linecache`, and so retrieves
    # the underlying notebook source instead of the generated Python code
    if set_except_hook:
        sys.excepthook = traceback.print_exception
