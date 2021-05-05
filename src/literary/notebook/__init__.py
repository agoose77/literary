"""Notebook helper namespace"""

__all__ = ["patch", "update_namespace"]

import pathlib as _pathlib

from . import importer as _importer
from .patch import patch
from .. import config as _config

_PACKAGE_ROOT_PATH = _config.find_project_path()

# Add root package to sys path & install import hook
_importer.install_hook(_PACKAGE_ROOT_PATH)


def update_namespace(namespace):
    """Update a namespace with the missing metadata required to support runtime
    imports of notebooks

    :param namespace: namespace object
    :return:
    """
    # In order for relative imports to work, we need to know the __package__ name of the
    # notebook.
    namespace["__package__"] = _importer.determine_package_name(
        _pathlib.Path.cwd(), _PACKAGE_ROOT_PATH
    )
