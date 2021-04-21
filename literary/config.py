import functools
import pathlib
from typing import Any, Dict
import configparser
import toml


PROJECT_ROOT_MARKERS = ("pyproject.toml", "setup.py", "setup.cfg", ".literary-project")


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


def load_pyproject_config(path: pathlib.Path) -> Dict[str, Any]:
    """Load configuration from a `tool.literary` section of a pyproject.toml
    file, modifying the various parameters where appropriate.

    :param path: path to pyproject.toml file
    :return:
    """
    project_path = path.parent.absolute()
    data = toml.load(path)

    config = {
        k.replace("-", "_"): v
        for k, v in data.get("tool", {}).get("literary", {}).items()
    }

    return load_config_from_dict(project_path, config)


def load_setup_cfg_config(path: pathlib.Path) -> Dict[str, Any]:
    """Load configuration from the `literary` section of a setup.cfg file,
    modifying the various parameters where appropriate.

    :param path: path to setup.cfg file
    :return:
    """
    project_path = path.parent.absolute()

    parser = configparser.ConfigParser()
    parser.read(path)

    if parser.has_section("literary"):
        config = dict(parser.items("literary"))
    else:
        config = {}

    return load_config_from_dict(project_path, config)


def load_config_from_dict(
    project_path: pathlib.Path, config: Dict[str, Any]
) -> Dict[str, Any]:

    source_path = config.get("source_path")
    if source_path is not None:
        source_path = (project_path / source_path).resolve()

    package_path = config.get("package_path")
    if package_path is not None:
        package_path = (project_path / package_path).resolve()

    test_paths = config.get("test_paths", [])
    if test_paths:
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

    setup_cfg_path = project_path / "setup.cfg"
    if setup_cfg_path.exists():
        return load_setup_cfg_config(setup_cfg_path)

    return {}
