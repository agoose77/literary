import ast
import sys
import logging

import traitlets.config
from jinja2 import DictLoader
from nbconvert import exporters
from traitlets import default, import_item, List

from .preprocessor import LiteraryPythonPreprocessor
from .utils import escape_triple_quotes

logger = logging.getLogger(__name__)

# Backwards compatibility
if sys.version_info < (3, 9, 0):
    import astunparse
    import astunparse.unparser

    class ASTUnparser(astunparse.unparser.Unparser):
        """AST unparser with additional preference for triple-quoted multi-line strings"""

        def _Constant(self, tree):
            if isinstance(tree.value, str) and "\n" in tree.value:
                self.write(f'"""{escape_triple_quotes(tree.value)}"""')
                return

            super()._Constant(tree)

    # Monkey patch to ensure correctness
    astunparse.Unparser = ASTUnparser
    astunparse.unparser.Unparser = ASTUnparser

    from astunparse import unparse as unparse_ast

else:
    from ast import unparse as unparse_ast


class LiteraryPythonExporter(exporters.PythonExporter):
    def __init__(self, *args, **kwargs):
        """
        Public constructor

        Parameters
        ----------
        config : ``traitlets.config.Config``
            User configuration instance.
        `**kw`
            Additional keyword arguments passed to parent __init__

        """

        super().__init__(*args, **kwargs)

        self._init_transformers()

    transformers = List(
        [
            "literary.transformers.PatchTransformer",
            "literary.transformers.IPythonTransformer",
        ]
    ).tag(config=True)

    def _init_transformers(self):
        self._transformers = []

        for value in self.transformers:
            if isinstance(value, str):
                value = import_item(value)
            self._transformers.append(value())

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
{{ cell.source | escape_triple_quotes }}
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

    def default_filters(self):
        yield from super().default_filters()
        yield "escape_triple_quotes", escape_triple_quotes

    def from_notebook_node(self, nb, resources=None, **kwargs):
        body, resources = super().from_notebook_node(nb, resources, **kwargs)
        node = ast.parse(body)

        try:
            # Support ast.NodeTransformer and custom transformers using
            # `visit()` API
            for transformer in self._transformers:
                node = transformer.visit(node)
        except Exception as err:
            raise RuntimeError(
                f"An error occurred during AST transforming: {body}"
            ) from err

        return unparse_ast(node), resources
