import traitlets.config
from traitlets import default
from nbconvert import exporters
from jinja2 import DictLoader
from .preprocessor import LiteraryPythonPreprocessor


class LiteraryPythonExporter(exporters.PythonExporter):
    @default("template_file")
    def _template_file_default(self):
        return "literary"

    @default("extra_loaders")
    def _extra_loaders_default(self):
        loader = DictLoader(
            {
                "literary": '''
{%- extends 'python/index.py.j2' -%}

{% block header %}
"""
{%- for cell in nb.cells -%}
{%- if "docstring" in cell.metadata.tags -%}
{{ cell.source }}
{% endif -%}
{%- endfor -%}
"""
{% endblock header %}

{%- block any_cell scoped -%}
{%- if "export" in cell.metadata.tags -%}
{{ super() }}
{%- endif -%}
{%- endblock any_cell -%}

                             '''
            }
        )
        return [loader]

    @default("default_preprocessors")
    def _default_preprocessors_default(self):
        return [LiteraryPythonPreprocessor]

    @default("exclude_input_prompt")
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
