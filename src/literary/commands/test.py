import logging
import pathlib
from concurrent import futures

from jupyter_core.application import JupyterApp
from traitlets import default, Unicode, List, Int

from .. import testing
from ..config import CONFIG_FILE_NAME

logger = logging.getLogger(__name__)

DEFAULT_IGNORE_PATTERNS = (".ipynb_checkpoints",)


def _patch_nbclient_exceptions():
    """Shim to patch nbclient exception pickling"""
    import nbclient.exceptions as exc

    # Fix https://github.com/jupyter/nbclient/issues/121
    def reduce_CellExecutionError(self):
        return type(self), (self.traceback, self.ename, self.evalue)

    exc.CellExecutionError.__reduce__ = reduce_CellExecutionError


def find_notebooks(path, ignore_patterns=None):
    """Find notebooks given by a particular path.

    If the path is a directory, yield from the result of calling find_notebooks` with
    the directory path.
    If the path is a notebook file path, yield the path directly

    :param path: path to a file or directory
    :param ignore_patterns: set of patterns to ignore during recursion
    :return:
    """
    if ignore_patterns is None:
        ignore_patterns = DEFAULT_IGNORE_PATTERNS

    if path.is_dir():
        for p in path.iterdir():
            # Ignore certain files and directories e.g. .ipynb_checkpoints
            if any(path.match(p) for p in ignore_patterns):
                continue

            yield from find_notebooks(p, ignore_patterns)

    elif path.match("*.ipynb"):
        yield path


class LiteraryTestApp(JupyterApp):
    name = "literary test"
    description = "Test literary notebooks in parallel"
    aliases = {
        **JupyterApp.aliases,
        "source": "LiteraryTestApp.source",
        "jobs": "LiteraryTestApp.jobs",
        "ignore": "LiteraryTestApp.ignore",
    }

    source = List(trait=Unicode(help="source directory or notebooks to run")).tag(
        config=True
    )
    jobs = Int(
        allow_none=True, default_value=None, help="number of parallel jobs to run"
    ).tag(config=True)
    ignore = List(help="glob pattern to ignore during recursion", trait=Unicode()).tag(
        config=True
    )

    @default("config_file_name")
    def _config_file_name_default(self):
        return CONFIG_FILE_NAME

    def start(self):
        if not self.source:
            raise ValueError(f"Missing source path(s)")

        source = [pathlib.Path(s) for s in self.source]
        paths = [p.resolve() for s in source for p in find_notebooks(s, self.ignore)]

        with futures.ProcessPoolExecutor(
            max_workers=self.jobs, initializer=_patch_nbclient_exceptions
        ) as executor:
            tasks = [executor.submit(testing.run_notebook, p) for p in paths]
            for task in futures.as_completed(tasks):
                task.result()
