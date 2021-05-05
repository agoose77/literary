import pathlib

from jupyter_core.application import JupyterApp
from traitlets import default, Unicode, List

from ..config import CONFIG_FILE_NAME
from ..package import build_package


class LiteraryBuildApp(JupyterApp):
    name = "literary build"
    description = "Build a pure-Python package from a set of Jupyter notebooks"
    aliases = {
        **JupyterApp.aliases,
        "source": "LiteraryBuildApp.source",
        "package": "LiteraryBuildApp.package",
        "ignore": "LiteraryBuildApp.ignore",
    }

    source = Unicode(help="source directory for notebooks").tag(config=True)
    package = Unicode(help="destination path generated package").tag(config=True)
    ignore = List(help="glob pattern to ignore during recursion", trait=Unicode()).tag(
        config=True
    )

    @default("config_file_name")
    def _config_file_name_default(self):
        return CONFIG_FILE_NAME

    def start(self):
        if not self.source:
            raise ValueError(f"Missing source path")

        source = pathlib.Path(self.source)
        if not self.package:
            raise ValueError(f"Missing package path")
        package = pathlib.Path(self.package)

        build_package(source, package, self.ignore)
