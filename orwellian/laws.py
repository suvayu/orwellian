from __future__ import annotations

import abc
from dataclasses import fields, is_dataclass, MISSING
import sys
import types
from typing import Callable, Iterable, Type, TypeVar

obj_t = TypeVar("obj_t")
val_t = TypeVar("val_t")


class Base(abc.ABC):
    """Dataclasses should derive from this to support nested dataclasses"""

    def __post_init__(self):
        for fld in fields(self):
            if is_dataclass(fld.type):
                defaults = {}
                for _fld in fields(fld.type):
                    if _fld.default != MISSING:
                        val = _fld.default
                    elif _fld.default_factory != MISSING:
                        val = _fld.default_factory()
                    else:
                        continue
                    defaults[_fld.name] = val
                kwargs = getattr(self, fld.name)
                setattr(self, fld.name, fld.type(**{**defaults, **kwargs}))


class Law(abc.ABC):
    default = None

    def __set_name__(self, owner: obj_t, attr: str) -> None:
        self.attr = f"_{attr}"

    def __get__(self, obj: obj_t, objtype: Type[obj_t] | None = None) -> val_t:
        return getattr(obj, self.attr)

    def __set__(self, obj: obj_t, val: val_t) -> None:
        self._obj = obj

        # when dataclass is instantiated w/ default arguments
        if val is self:
            if self.default is None:
                raise ValueError(
                    f"{self.attr[1:]!r}: missing value, doesn't have a default"
                )
            else:
                val = self.default  # type: ignore

        # set before validation, easier dependent validations
        setattr(obj, self.attr, val)
        self.__validate_type__(val)
        self.__validate__(val)

    def __validate_type__(self, val: val_t) -> val_t:
        attr = self.attr[1:]  # drop leading underscore
        tp = self._obj.__annotations__[attr]
        if isinstance(val, tp):
            return val
        raise TypeError(f"{attr!r}: type mismatch: {type(val)} is not {tp}")

    @abc.abstractmethod
    def __validate__(self, val: val_t) -> val_t:  # pragma: no cover, virtual
        return val


class OneOf(Law):
    def __init__(self, allowed: Iterable, default=None):
        self.default = default
        self.allowed = set(allowed)

    def __validate__(self, val: val_t) -> val_t:
        if val not in self.allowed:
            raise ValueError(f"{val} not in {self.allowed}")
        return val


class IsRange(Law):
    def __init__(self, lo: str):
        self.lo = lo

    def __validate__(self, val: val_t) -> val_t:
        lo = getattr(self._obj, self.lo)
        if lo > val:
            raise ValueError(f"{self.lo} ({lo}) > {val}")
        return val


def legislate(name: str, func: Callable, **kwargs) -> Type[Law]:
    def __validate__(self, val):
        return func(self, val, **kwargs)

    bases = [Law]
    namespace = {"__validate__": __validate__}

    law = types.new_class(name, bases, {}, lambda ns: ns.update(namespace))
    if sys.version_info.minor >= 10:
        return abc.update_abstractmethods(law)
    else:
        return law
