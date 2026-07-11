# -*- coding: utf-8 -*-
"""

graphtransliterator.transliterators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Bundled transliterators are loaded by explicitly importing
:mod:`graphtransliterator.transliterators`. Each is an instance of
:mod:`graphtransliterator.bundled.Bundled`.
"""

import importlib.util
import inspect
import pkgutil
import sys

from .bundled import Bundled  # noqa
from .schemas import MetadataSchema  # noqa

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

        # --- FIX: Modern importlib implementation ---
        # 1. Get the module's specification using the modern finder API
        spec = loader.find_spec(module_name)
        if spec is None:
            continue

        # 2. Create the module object from the specification
        _module = importlib.util.module_from_spec(spec)

        # 3. Cache it in sys.modules (best practice for standard behavior)
        sys.modules[module_name] = _module

        # 4. Execute the module to fully load its contents
        spec.loader.exec_module(_module)
        # ---------------------------------------------

        for name, _obj in inspect.getmembers(_module, inspect.isclass):
            # Skip Bundled, as it is already loaded
            # Skip any classes starting with _
            if _skip_class_name(name):
                continue
            if name in __all__:
                raise ValueError('A transliterator named "{}" already exists'.format(name))
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
    for name in iter_names():
        cls = globals().get(name)
        if cls:
            yield cls(**kwds)
