"""
graphtransliterator.transliterators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import importlib.util
import inspect
import pkgutil
import sys
from collections.abc import Iterator
from typing import Any, cast

from graphtransliterator import GraphTransliterator
from graphtransliterator.transliterators.bundled import Bundled  # Import Bundled base class

from .schemas import MetadataSchema

__all__ = ["Bundled", "MetadataSchema", "iter_names", "iter_transliterators"]

# FIX: Use built-in list instead of typing.List
_transliterators: list[str] = []


def _skip_class_name(name: str) -> bool:
    """Determine if the class name should be skipped."""
    return name == "Bundled" or name.startswith("_")


def add_transliterators(path: list[str] | Any = None) -> None:
    """Walk submodules and loads bundled transliterators into namespace."""

    if path is None:
        path = __path__

    for loader, module_name, is_pkg in pkgutil.walk_packages(path):
        if not is_pkg:
            continue

        # FIX: Type check loader to satisfy MetaPathFinderProtocol and avoid union-attr issues
        if hasattr(loader, "find_spec"):
            # Provide the optional second argument to pass strict Mypy checks
            spec = loader.find_spec(module_name, None)
            if spec is None or spec.loader is None:
                continue

            _module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = _module
            spec.loader.exec_module(_module)

            for name, _obj in inspect.getmembers(_module, inspect.isclass):
                if _skip_class_name(name):
                    continue
                if name in __all__:
                    raise ValueError(f'A transliterator named "{name}" already exists')

                assert len(cast(Any, _module).__path__) == 1
                globals()[name] = getattr(_module, name)
                __all__.append(name)
                _transliterators.append(name)


add_transliterators()


def iter_names() -> Iterator[str]:
    """Iterate through bundled bundled transliterator names."""
    yield from _transliterators


def iter_transliterators(**kwds):
    """Yield instances of all bundled GraphTransliterator subclasses."""
    for name, cls in inspect.getmembers(sys.modules[__name__]):
        if (
            isinstance(cls, type)
            and issubclass(cls, GraphTransliterator)
            # Exclude base classes that require __init__ arguments
            and cls not in (GraphTransliterator, Bundled)
        ):
            yield cls(**kwds)
