import logging
import pathlib

import nbclient
import nbformat

logger = logging.getLogger(__name__)


def run_notebook(path: pathlib.Path, cell_timeout: int = 20):
    """Run a Jupyter notebook at the given path

    :param path: path to notebook
    :param cell_timeout: timeout for each cell execution
    :return:
    """
    try:
        logger.info(f"Executing {path}")
        nb = nbformat.read(path, as_version=nbformat.NO_CONVERT)
        client = nbclient.NotebookClient(
            nb, timeout=cell_timeout, resources={"metadata": {"path": path.parent}}
        )
        client.execute()
        logger.info(f"Finished executing {path}")
    except Exception:
        logger.exception(f"Error during execution of {path}")
        raise
