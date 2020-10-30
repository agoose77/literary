import traitlets.config
from nbconvert import exporters

from .preprocessor import LiteraryPythonPreprocessor


class LiteraryPythonExporter(exporters.PythonExporter):
    @traitlets.default("default_preprocessors")
    def _default_preprocessors_default(self):
        return [LiteraryPythonPreprocessor]

    @traitlets.default("exclude_input_prompt")
    def _exclude_input_prompt_default(self):
        return True

    @property
    def default_config(self):
        c = traitlets.config.Config(
            {
                "LiteraryPythonPreprocessor": {"enabled": True},
            }
        )
        c.merge(super().default_config)
        return c
