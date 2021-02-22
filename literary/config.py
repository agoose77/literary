import functools
import pathlib
from typing import Any, Dict

import toml


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

            if (path / ".git").exists():
                return path

            if (path / ".hg").exists():
                return path

            if (path / "pyproject.toml").exists():
                return path

    raise FileNotFoundError("Couldn't find project path")


def load_pyproject_config(path: pathlib.Path) -> Dict[str, Any]:
    """Load configuration from a pyproject.toml file, modifying the various parameters
    where appropriate.

    :param path: path to pyproject.toml file
    :return:
    """
    data = toml.load(path)
    project_path = path.parent.absolute()

    config = {
        k.replace("-", "_"): v
        for k, v in data.get("tool", {}).get("literary", {}).items()
    }

    if (source_path := config.get("source_path")) is not None:
        source_path = (project_path / source_path).resolve()

    if (package_path := config.get("package_path")) is not None:
        package_path = (project_path / package_path).resolve()

    if test_paths := config.get("test_paths", []):
        test_paths = [(project_path / p).resolve() for p in test_paths]

    test_processes = config.get("test_processes")

    return {
        "source_path": source_path,
        "package_path": package_path,
        "test_paths": test_paths,
        "test_processes": test_processes,
    }


def load_default_config(project_path: pathlib.Path) -> Dict[str, Any]:
    """Load configuration from a pyproject.toml file, returning an empty
    dictionary if the file does not exist

    :param project_path: path to pyproject.toml file
    :return:
    """
    pyproject_path = project_path / "pyproject.toml"
    if pyproject_path.exists():
        return load_pyproject_config(pyproject_path)
    return {}
