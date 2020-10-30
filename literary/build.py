import argparse
import pathlib
import nbformat
import traitlets
import shutil

from . import exporter


def create_notebook_code(nb_exporter, path: pathlib.Path) -> str:
    """Return the source code for a given notebook file

    :param nb_exporter: nbconvert exporter instance
    :param path: path to notebook
    :return:
    """
    nb = nbformat.read(path, as_version=nbformat.NO_CONVERT)
    body, resources = nb_exporter.from_notebook_node(nb)
    return body


def build_package_component(
    nb_exporter,
    source_dir_path,
    dest_dir_path,
    ignore_patterns=frozenset((".ipynb_checkpoints", "__pycache__", ".*")),
):
    """Recursively build a pure-Python package from a source tree

    :param nb_exporter: nbconvert exporter instance
    :param source_dir_path: path to current source directory
    :param dest_dir_path: path to current destination directory
    :param ignore_patterns: Glob patterns of files to ignroe
    :return:
    """
    for path in source_dir_path.iterdir():
        # Ignore any unwanted files or directories
        if any(path.match(p) for p in ignore_patterns):
            continue

        relative_path = path.relative_to(source_dir_path)

        # Rewrite notebook in target directory
        if path.match("*.ipynb"):
            dest_path = dest_dir_path / relative_path.with_suffix(".py")

            source = create_notebook_code(nb_exporter, path)
            dest_path.write_text(source)

        # Recurse into directory
        elif path.is_dir():
            dest_path = dest_dir_path / relative_path
            dest_path.mkdir(parents=True, exist_ok=True)
            build_package_component(nb_exporter, path, dest_path)

        # Copy file directly
        else:
            dest_path = dest_dir_path / relative_path
            dest_path.write_bytes(
                path.read_bytes(),
            )


def build_package(source_path: pathlib.Path, dest_root_path: pathlib.Path):
    """Build a pure-Python package from a literary source tree

    :param source_path: path to notebooks directory
    :param dest_root_path: path to directory in which to generate package
    :return:
    """
    c = traitlets.config.Config()
    nb_exporter = exporter.LiteraryPythonExporter(config=c)

    dest_path = dest_root_path / source_path.name
    if dest_path.exists():
        shutil.rmtree(dest_path)
    dest_path.mkdir()

    build_package_component(nb_exporter, source_path, dest_path)


def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=pathlib.Path)
    parser.add_argument("dest_root", type=pathlib.Path)
    args = parser.parse_args(argv)

    build_package(args.source, args.dest_root)
