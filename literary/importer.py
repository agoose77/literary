import importlib.machinery
import pathlib
import sys

import nbformat
import traitlets.config

from .exporter import LiteraryPythonExporter


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

        for entry in path:
            notebook_path = pathlib.Path(entry) / f"{fullname}.ipynb"
            if notebook_path.exists():
                spec = importlib.machinery.ModuleSpec(
                    fullname, NotebookLoader(notebook_path), origin=str(notebook_path)
                )
                spec.has_location = True
                return spec


def install_hook(path=None):
    if path is None:
        path = sys.path
    sys.meta_path.append(NotebookFinder(path))
