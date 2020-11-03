from typing import Callable, Type, TypeVar

T = TypeVar("T")


def patch(cls: Type) -> Callable[[T], T]:
    """Decorator to monkey-patch additional methods to a class.

    At import-time, this will disappear and the source code itself will be transformed
    Inside notebooks, the implementation below will be used.

    :param cls:
    :return:
    """

    def _notebook_patch_impl(func):
        setattr(cls, func.__name__, func)
        return func

    return _notebook_patch_impl
