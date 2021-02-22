from typing import Callable, Type, TypeVar

T = TypeVar("T")


def patch(cls: Type) -> Callable[[T], T]:
    """Decorator to monkey-patch additional methods to a class.

    At import-time, this will disappear and the source code itself will be transformed
    Inside notebooks, the implementation below will be used.

    :param cls:
    :return:
    """

    def get_name(func):
        # Fix #4 to support patching (property) descriptors
        try:
            return func.__name__
        except AttributeError:
            # Support various descriptors
            for attr in "fget", "fset", "fdel", "__func__":
                try:
                    return getattr(func, attr).__name__
                except AttributeError:
                    continue

            # Raise original exception
            raise

    def _notebook_patch_impl(func):
        setattr(cls, get_name(func), func)
        return func

    return _notebook_patch_impl
