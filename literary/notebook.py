import pathlib
import sys

from .importer import find_package_root, install_hook

_CWD_PATH = pathlib.Path.cwd()
_PACKAGE_ROOT_PATH = find_package_root(_CWD_PATH)

# The package root path must be on the system path
sys.path.append(str(_PACKAGE_ROOT_PATH))
# To avoid bad practice, prevent cwd being used for lookups, both explicitly
# or from empty strings
sys.path = [p for p in sys.path if pathlib.Path(p) != _CWD_PATH and p]


def _determine_package_name(package_root_path: pathlib.Path) -> str:
    relative_path = pathlib.Path.cwd().relative_to(package_root_path)
    return ".".join(relative_path.parts)


# In order for relative imports to work, we need to know the __package__ name of the
# notebook. This is imported using %run in notebooks
__package__ = _determine_package_name(_PACKAGE_ROOT_PATH)


# Install import hook
install_hook()
