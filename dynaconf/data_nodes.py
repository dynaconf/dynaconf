from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from typing import Union

import dynaconf.utils as ut


class DynaconfNotInitialized(BaseException): ...


class DynaconfCore:
    def __init__(self, id: str):
        self.id = id

    def edit_mode(self):
        return False


@dataclass
class NodeMetadata:
    """
    The namespace for any internal state of the data-node.
    """

    core: Optional[DynaconfCore] = None
    data_env: str = "default"


# Utilities for manipulating Data nodes.

# Adding those directly to the data nodes causes some overhead and clutters
# the class namespace. It should be as close as possible to 'dict'.


def init_core(node, dynaconf_core: DynaconfCore):
    if not node.__meta__.core:
        node.__meta__.core = dynaconf_core


def get_core(node, raises=True) -> DynaconfCore:
    dynaconf_core = node.__meta__.core
    if not dynaconf_core and raises is True:
        raise DynaconfNotInitialized("Dynaconf not initialized.")
    return dynaconf_core


def convert_containers(data: dict | list | DataNode, iter, core):
    for key, value in iter:
        if isinstance(value, dict):
            data[key] = DataDict(value, core=core)
        elif isinstance(value, list):
            data[key] = DataList(value, core=core)


def ensure_containers(data, core):
    if data.__class__ is dict:
        return DataDict(data, core=core)
    elif data.__class__ is list:
        return DataList(data, core=core)
    return data


class DataDict(dict):
    __slots__ = ("__meta__",)

    def __init__(self, *args, **kwargs):
        core = kwargs.pop("box_settings", kwargs.pop("core", None))
        super().__init__(*args, **kwargs)
        self.__meta__ = NodeMetadata(core=core)
        convert_containers(self, self.items(), core)

    def update(self, data):
        super().update(ensure_containers(data, self.__meta__.core))

    def setdefault(self, k, v):
        return super().setdefault(k, ensure_containers(v, self.__meta__.core))

    def copy(self):
        return self.__class__(super().copy())

    def get(self, k, default=None):
        resolved = ut.find_the_correct_casing(key=k, data=self)
        return super().get(resolved, default)

    def __copy__(self):
        return self.__class__(super().copy())

    def __getitem__(self, k):
        resolved = ut.find_the_correct_casing(key=k, data=self)
        return super().__getitem__(resolved)

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(attr) from None

    def __setitem__(self, k, v):
        super().__setitem__(k, ensure_containers(v, self.__meta__.core))

    def __setattr__(self, k, v):
        if k == "__meta__":
            return super().__setattr__(k, v)
        self[k] = v

    def __repr__(self):
        return f"{self.__class__.__name__}({dict(self)})"

    # Box compatibility. Remove in 3.3.0
    def to_dict(self):
        """Convert to regular dict"""
        pass

    def merge_update(self, *args, **kwargs):
        """Merge update with another dict"""
        if args:
            other = args[0]
            if hasattr(other, "keys"):
                for key in other:
                    if key in self:
                        self[key] = ut.object_merge(self[key], other[key])
                    else:
                        self[key] = other[key]
            else:
                raise TypeError(
                    "merge_update expected at most 1 arguments, got more"
                )

        for key, value in kwargs.items():
            if key in self:
                self[key] = ut.object_merge(self[key], value)
            else:
                self[key] = value

    def to_json(self, *args, **kwargs):
        """Convert to JSON string"""
        pass

    def to_yaml(self, *args, **kwargs):
        """Convert to YAML string"""
        pass

    def to_toml(self, *args, **kwargs):
        """Convert to TOML string"""
        pass

    @classmethod
    def from_json(cls, json_str, *args, **kwargs):
        """Create from JSON string"""
        pass

    @classmethod
    def from_yaml(cls, yaml_str, *args, **kwargs):
        """Create from YAML string"""
        pass

    @classmethod
    def from_toml(cls, toml_str, *args, **kwargs):
        """Create from TOML string"""
        pass


class DataList(list):
    __slots__ = ("__meta__",)

    def __init__(self, *args, **kwargs):
        core = kwargs.pop("box_settings", kwargs.pop("core", None))
        super().__init__(*args, **kwargs)
        self.__meta__ = NodeMetadata(core=core)
        convert_containers(self, enumerate(self), core)

    def copy(self):
        return self.__class__(super().copy())

    def append(self, v):
        super().append(ensure_containers(v, self.__meta__.core))

    def insert(self, i, v):
        super().insert(i, ensure_containers(v, self.__meta__.core))

    def extend(self, data):
        super().extend(ensure_containers(data, self.__meta__.core))

    def __setitem__(self, k, v):
        super().__setitem__(k, ensure_containers(v, self.__meta__.core))

    def __add__(self, v):
        super().__add__(ensure_containers(v, self.__meta__.core))

    def __iadd__(self, v):
        return super().__iadd__(ensure_containers(v, self.__meta__.core))

    def __repr__(self):
        return f"{self.__class__.__name__}({list(self)!r})"

    # Box compatibility. Remove in 3.3.0
    def __copy__(self, memo):
        """Copy support"""
        pass

    def __deepcopy__(self, memo):
        """Deep copy support"""
        pass

    def to_list(self):
        """Convert to regular list"""
        pass

    def to_json(self, *args, **kwargs):
        """Convert to JSON string"""
        pass

    def to_yaml(self, *args, **kwargs):
        """Convert to YAML string"""
        pass

    def to_toml(self, *args, **kwargs):
        """Convert to TOML string"""
        pass

    def to_csv(self, *args, **kwargs):
        """Convert to CSV string"""
        pass

    @classmethod
    def from_json(cls, json_str, *args, **kwargs):
        """Create from JSON string"""
        pass

    @classmethod
    def from_yaml(cls, yaml_str, *args, **kwargs):
        """Create from YAML string"""
        pass

    @classmethod
    def from_toml(cls, toml_str, *args, **kwargs):
        """Create from TOML string"""
        pass

    @classmethod
    def from_csv(cls, csv_str, *args, **kwargs):
        """Create from CSV string"""
        pass


DataNode = Union[DataDict, DataList]
