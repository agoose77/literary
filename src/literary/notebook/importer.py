import importlib.machinery
import inspect
import linecache
import os
import pathlib
import sys
import traceback
from typing import AnyStr, Any, Callable, Tuple, TypeVar, Union

import nbformat

from ..config import load_config
from ..exporter import LiteraryPythonExporter


class NotebookLoader(importlib.machinery.SourcelessFileLoader):
    """Sourceless Jupyter Notebook loader"""

    def __init__(self, fullname: str, path: str, config):
        super().__init__(fullname, path)

        self._config = config

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
        return compile(body, path, "exec")

    def get_transpiled_source(self, path: str):
        nb = nbformat.read(path, as_version=nbformat.NO_CONVERT)
        exporter = LiteraryPythonExporter(config=self._config)
        body, resources = exporter.from_notebook_node(nb)
        return body


def determine_package_name(path: pathlib.Path, package_root_path: pathlib.Path) -> str:
    """Determine the corresponding importable name for a package directory given by
    a particular file path

    :param path: path to package
    :param package_root_path: root path containing notebook package directory
    :return:
    """
    relative_path = path.relative_to(package_root_path)
    return ".".join(relative_path.parts)


def _get_loader_details(hook) -> tuple:
    """Return the loader_details for a given FileFinder closure

    :param hook: FileFinder closure
    :returns: loader_details tuple
    """
    try:
        namespace = inspect.getclosurevars(hook)
    except TypeError as err:
        raise ValueError from err

    try:
        return namespace.nonlocals["loader_details"]
    except KeyError as err:
        raise ValueError from err


def _find_file_finder(path_hooks: list) -> Tuple[int, Any]:
    """Find the FileFinder closure in a list of path hooks

    :param path_hooks: path hooks
    :returns: index of hook and the hook itself
    """
    for i, hook in enumerate(path_hooks):
        try:
            _get_loader_details(hook)
        except ValueError:
            continue

        return i, hook
    raise ValueError


T = TypeVar("T")


def _extend_file_finder(finder: T, *loader_details) -> T:
    """Extend an existing file finder with new loader details

    :param finder: existing FileFinder instance
    :param loader_details:
    :return:
    """
    return importlib.machinery.FileFinder.path_hook(
        *_get_loader_details(finder), *loader_details
    )


def _inject_notebook_loader(
    path_hooks: list, loader_factory: Callable[[str, str], NotebookLoader]
):
    """Inject a NotebookLoader into a list of path hooks

    :param path_hooks: list of path hooks
    :param loader_factory: factory to to create NotebookLoader
    :return:
    """
    i, finder = _find_file_finder(path_hooks)
    new_finder = _extend_file_finder(finder, (loader_factory, [".ipynb"]))
    path_hooks[i] = new_finder

    # To fix cached path finders
    sys.path_importer_cache.clear()


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
    # Load config for project
    config = load_config(package_root_path)

    # Make notebook packages importable by adding package root path to sys.path
    sys.path.append(str(package_root_path))

    # Create notebook loader factory
    def create_notebook_loader(fullname, path):
        return NotebookLoader(fullname, path, config)

    # Inject notebook loader into path_hooks
    _inject_notebook_loader(sys.path_hooks, create_notebook_loader)

    # Python's C-level traceback reporting doesn't call `linecache`, and so retrieves
    # the underlying notebook source instead of the generated Python code
    if set_except_hook:
        sys.excepthook = traceback.print_exception
