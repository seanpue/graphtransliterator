# -*- coding: utf-8 -*-
"""

graphtransliterator.transliterators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Bundled transliterators are loaded by explicitly importing
:mod:`graphtransliterator.transliterators`. Each is an instance of
:mod:`graphtransliterator.bundled.Bundled`.
"""
from .bundled import Bundled  # noqa
from .schemas import MetadataSchema  # noqa
import inspect
import pkgutil

__all__ = ["Bundled", "MetadataSchema", "iter_names", "iter_transliterators"]

_transliterators = []


def _skip_class_name(name):
    """Determine if the class name should be skipped."""
    return name == "Bundled" or name.startswith("_")


def add_transliterators(path=__path__):
    """Walk submodules and loads bundled transliterators into namespace.

    Bundled transliterators are stored as ``Bundled`` subclass.

    Parameters
    ----------
    path : list
        List of paths, must be an iterable of strings

    Raises
    ------
    ValueError
        A transliterator of the same name already has been loaded."""

    for loader, module_name, is_pkg in pkgutil.walk_packages(path):
        # if it is not a submodule, skip it.
        if not is_pkg:
            continue
        _module = loader.find_module(module_name).load_module(module_name)

        for name, _obj in inspect.getmembers(_module, inspect.isclass):
            # Skip Bundled, as it is already loaded
            # Skip any classes starting with _
            if _skip_class_name(name):
                continue
            if name in __all__:
                raise ValueError(
                    'A transliterator named "{}" already exists'.format(name)
                )
            # import module and add class to globals, so that it will show up as
            # graphtransliterator.transliterators.TRANSLITERATORNAME
            assert len(_module.__path__) == 1  # There should be only one path
            globals()[name] = getattr(_module, name)
            __all__.append(name)
            _transliterators.append(name)


add_transliterators()


def iter_names():
    """Iterate through bundled transliterator names."""
    for _ in _transliterators:
        yield _


def iter_transliterators(**kwds):
    """Iterate through instances of bundled transliterators."""
    for _ in iter_names():
        yield (eval(_ + "()"))
