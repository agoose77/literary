import sys

from jupyter_core.application import JupyterApp
from traitlets import default

from .commands import build, test
from .config import CONFIG_FILE_NAME


class LiteraryApp(JupyterApp):
    name = "literary"
    description = "Work with literate notebooks"
    subcommands = {
        "build": (build.LiteraryBuildApp, "Build a package from a series of notebooks"),
        "test": (test.LiteraryTestApp, "Run a series of notebook tests"),
    }

    @default("config_file_name")
    def config_file_name_default(self):
        return CONFIG_FILE_NAME

    def start(self):
        """Perform the App's actions as configured"""
        super().start()

        # The above should have called a subcommand and raised NoStart; if we
        # get here, it didn't, so we should self.log.info a message.
        sub_commands = ", ".join(sorted(self.subcommands))
        sys.exit("Please supply at least one subcommand: {}".format(sub_commands))


launch_new_instance = LiteraryApp.launch_instance
