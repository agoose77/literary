import functools
import pathlib
from jupyter_core.paths import jupyter_config_path
import traitlets.config

CONFIG_FILE_NAME = "literary_config"
PROJECT_ROOT_MARKERS = (
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    ".literary-project",
    f"{CONFIG_FILE_NAME}.json",
    f"{CONFIG_FILE_NAME}.py",
)


def load_config(project_path: pathlib.Path) -> traitlets.config.Config:
    """Load the literary config file, or return an empty config object if missing"""
    paths = [project_path, *jupyter_config_path()]
    loaders = [
        traitlets.config.JSONFileConfigLoader(f"{CONFIG_FILE_NAME}.json", path=paths),
        traitlets.config.PyFileConfigLoader(f"{CONFIG_FILE_NAME}.py", path=paths),
    ]
    config = traitlets.config.Config()
    for loader in loaders:
        try:
            config.update(loader.load_config())
        except traitlets.config.ConfigFileNotFound:
            pass

    return config


@functools.lru_cache()
def find_project_path(*search_paths) -> pathlib.Path:
    """Find the root path of the literary project.

    Searches for known files / directories including
    `.git/`, `.hg/`, or `pyproject.toml`.

    :param search_paths: starting search paths
    :return:
    """
    if not search_paths:
        search_paths = [pathlib.Path.cwd()]

    visited = set()

    for search_path in search_paths:
        for path in (search_path, *search_path.parents):
            # Avoid re-visiting paths
            if path in visited:
                break
            visited.add(path)

            # Look for any Python package marker
            for marker in PROJECT_ROOT_MARKERS:
                if (path / marker).exists():
                    return path

    raise FileNotFoundError("Couldn't find project path")
