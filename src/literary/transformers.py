import ast
import logging
from typing import Any, Dict, Iterable, TypeVar

import traitlets.config

logger = logging.getLogger(__name__)

T = TypeVar("T")


class IPythonTransformer(traitlets.config.Configurable):
    """Node transformer which operates upon ast.Module nodes to check for IPython
    statements.
    """

    error_if_ipython = traitlets.Bool(default_value=True).tag(config=True)

    def visit(self, node: ast.Module) -> ast.Module:
        """Transform a Python module AST node

        :param node: ast.Module object
        :return: ast.Module object
        """
        for descendant in ast.walk(node):
            if not isinstance(descendant, ast.Call):
                continue

            if not isinstance(descendant.func, ast.Name):
                continue

            if descendant.func.id == "get_ipython":
                msg = (
                    "`get_ipython` cannot be transpiled to pure-Python. "
                    "Check for magics in exported code cells"
                )
                if self.error_if_ipython:
                    raise ValueError(msg)
                else:
                    logger.warning(msg)

        return node


class PatchTransformer(traitlets.config.Configurable):
    """Node transformer which operates upon ast.Module nodes to handle patches."""

    patch_decorator_id = traitlets.Unicode("patch").tag(config=True)

    def _is_patch_decorator(self, node: Any) -> bool:
        """Return True if the given ast node is a patch() decorator

        :param node: ast node
        :return:
        """
        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == self.patch_decorator_id
        )

    def _apply_patches_to_node(self, decorated: Any, classes: Dict[str, Any]):
        """Append patch functions to body of patched class.

        :param decorated: decorated function node
        :param classes: mapping of name to class node
        :return: whether node should be removed from original AST location
        """
        patch_decorators = []
        other_decorators = []

        for node in decorated.decorator_list:
            if self._is_patch_decorator(node):
                if other_decorators:
                    raise ValueError(
                        "Applying decorators to a patched function is not "
                        "safe at runtime, and is hence prohibited."
                    )
                patch_decorators.append(node)
            else:
                other_decorators.append(node)

        if not patch_decorators:
            return False

        logger.info(f"Found patch function {ast.dump(decorated)}")
        decorated.decorator_list = other_decorators

        # Copy decorated node to destination body
        for node in reversed(patch_decorators):
            (patched_name_node,) = node.args
            patched_node = classes[patched_name_node.id]
            patched_node.body.append(decorated)
            logger.debug(f"Patching {patched_node.name} with {ast.dump(decorated)}")

        return True

    def _transform_module_body(self, nodes: Iterable[T]) -> Iterable[T]:
        """Transform the nodes of an ast.Module to handle patches.

        :param nodes: iterable of ast nodes
        :return:
        """
        classes = {}
        for child in nodes:
            if isinstance(child, ast.ClassDef):
                classes[child.name] = child

            # If there were patch decorators, don't keep this node
            if hasattr(child, "decorator_list") and self._apply_patches_to_node(
                child, classes
            ):
                continue

            yield child

    def visit(self, node: ast.Module) -> ast.Module:
        """Transform a Python module AST node.

        :param node: ast.Module object
        :return: ast.Module object
        """
        node.body = [*self._transform_module_body(node.body)]
        ast.fix_missing_locations(node)
        return node
