import argparse
import logging
import pathlib
from concurrent.futures import ProcessPoolExecutor

import nbclient
import nbformat

logger = logging.getLogger(__name__)


def run_notebook(path: pathlib.Path, cell_timeout: int = 120):
    logger.debug(f"Executing {path}")
    nb = nbformat.read(path, as_version=nbformat.NO_CONVERT)
    client = nbclient.NotebookClient(
        nb, timeout=cell_timeout, resources={"metadata": {"path": path.parent}}
    )
    client.execute()
    logger.debug(f"Finished executing {path}")


def run(argv=None):
    parser = argparse.ArgumentParser(description="Test literary notebooks in parallel")
    parser.add_argument(
        "source", type=pathlib.Path, help="source directory for notebooks"
    )
    parser.add_argument(
        "-j", "--jobs", default=None, type=int, help="number of " "parallel jobs to run"
    )
    args = parser.parse_args(argv)

    executor = ProcessPoolExecutor(max_workers=args.jobs)
    executor.map(run_notebook, args.source.glob("*.ipynb"))
    executor.shutdown()
