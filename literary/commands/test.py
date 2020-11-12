import logging
import pathlib
from concurrent import futures

from .. import config
from .. import testing

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


def configure(subparsers):
    project_config = config.load_default_config(config.find_project_path())

    parser = subparsers.add_parser(
        "test",
        description="Test literary notebooks in parallel",
    )
    parser.add_argument(
        "-s",
        "--source",
        type=pathlib.Path,
        default=[project_config["source_path"], *project_config["test_paths"]],
        action="append",
        help="path to notebook or directory (recursive)",
    )
    parser.add_argument(
        "-j",
        "--jobs",
        default=project_config["test_processes"],
        type=int,
        help="number of parallel jobs to run",
    )
    parser.add_argument(
        "-i",
        "--ignore",
        help="glob pattern to ignore during recursion",
        action="append",
    )
    return parser


def run(args):
    if args.source is None:
        raise ValueError(f"Invalid source path {args.source!r}")

    paths = set(
        p.resolve() for s in args.source for p in find_notebooks(s, args.ignore)
    )

    with futures.ProcessPoolExecutor(
        max_workers=args.jobs, initializer=_patch_nbclient_exceptions
    ) as executor:
        tasks = [executor.submit(testing.run_notebook, p) for p in paths]
        for task in futures.as_completed(tasks):
            task.result()
