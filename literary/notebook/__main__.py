__all__ = ["patch", "__package__"]

from . import importer as _importer
from . import paths as _paths
from .patch import patch

_PACKAGE_ROOT_PATH = _paths.find_package_root()
# In order for relative imports to work, we need to know the __package__ name of the
# notebook. This is imported using %run in notebooks
__package__ = _importer.determine_package_name(_PACKAGE_ROOT_PATH)


# Add root package to sys path & install import hook
_importer.install_hook(_PACKAGE_ROOT_PATH)
