# -*- coding: utf-8 -*-
"""
graphtransliterator.transliterators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import importlib.util
import inspect
import pkgutil
import sys
from typing import cast, Any, Iterator, List, Union

from .bundled import Bundled  # noqa
from .schemas import MetadataSchema  # noqa

__all__ = ["Bundled", "MetadataSchema", "iter_names", "iter_transliterators"]

# FIX: Add explicit type annotation to satisfy [var-annotated]
_transliterators: List[str] = []


def _skip_class_name(name: str) -> bool:
    """Determine if the class name should be skipped."""
    return name == "Bundled" or name.startswith("_")


def add_transliterators(path: Union[List[str], Any] = None) -> None:
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
                    raise ValueError('A transliterator named "{}" already exists'.format(name))
                
                assert len(cast(Any, _module).__path__) == 1
                globals()[name] = getattr(_module, name)
                __all__.append(name)
                _transliterators.append(name)


add_transliterators()


def iter_names() -> Iterator[str]:
    """Iterate through bundled bundled transliterator names."""
    for _ in _transliterators:
        yield _


def iter_transliterators(**kwds: Any) -> Iterator[Any]:
    for name in iter_names():
        cls = globals().get(name)
        if cls:
            yield cls(**kwds)