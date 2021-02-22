import ast
import types

import pytest

from literary.transformers import PatchTransformer

PREAMBLE_SOURCE = """
from literary.notebook.patch import patch
class SomeClass:
    pass
"""

PATCH_WRAP_METHOD_SOURCE = """
@patch(SomeClass)
def identity(self):
    return self
    """

PATCH_WRAP_PROPERTY_SOURCE = """
@patch(SomeClass)
@property
def identity(self):
    return self
    """

PROPERTY_WRAP_PATCH_SOURCE = """
@property
@patch(SomeClass)
def identity(self):
    return self
    """


def compile_and_exec(node_or_source, namespace=None):
    if namespace is None:
        namespace = {}
    code = compile(node_or_source, "<AST>", "exec")
    exec(code, namespace)
    return types.SimpleNamespace(**namespace)


def transform_compile_and_exec(source):
    node = ast.parse(source)
    new_node = PatchTransformer().visit(node)
    return compile_and_exec(new_node)


@pytest.mark.parametrize("compiler", [compile_and_exec, transform_compile_and_exec])
def test_patch_descriptors(compiler):
    ns = compiler(PREAMBLE_SOURCE + PATCH_WRAP_PROPERTY_SOURCE)
    obj = ns.SomeClass()

    assert hasattr(obj, "identity")
    assert obj.identity is obj


@pytest.mark.parametrize("compiler", [compile_and_exec, transform_compile_and_exec])
def test_patch_methods(compiler):
    ns = compiler(PREAMBLE_SOURCE + PATCH_WRAP_METHOD_SOURCE)
    obj = ns.SomeClass()

    assert hasattr(obj, "identity")
    assert obj.identity() is obj


def test_transformer_decorate_patched_method_prohibited():
    with pytest.raises(ValueError):
        transform_compile_and_exec(PREAMBLE_SOURCE + PROPERTY_WRAP_PATCH_SOURCE)
