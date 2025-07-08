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
        """
        Turn the DataDict and sub DataDicts back into a native python dictionary.

        :return: python dictionary of this DataDict
        """
        out_dict = dict(self)
        for k, v in out_dict.items():
            if v is self:
                out_dict[k] = out_dict
            elif isinstance(v, DataDict):
                out_dict[k] = v.to_dict()
            elif isinstance(v, DataList):
                out_dict[k] = v.to_list()
        return out_dict

    def merge_update(self, __m=None, **kwargs):
        """Merge update with another dict"""

        def convert_and_set(k, v):
            if isinstance(v, dict):
                v = self.__class__(v, core=self.__meta__.core)
                if k in self and isinstance(self[k], dict):
                    if isinstance(self[k], DataDict):
                        self[k].merge_update(v)
                    else:
                        self[k].update(v)
                    return
            if isinstance(v, list):
                v = DataList(v, core=self.__meta__.core)
            self.__setitem__(k, v)

        if __m:
            if hasattr(__m, "keys"):
                for key in __m:
                    convert_and_set(key, __m[key])
            else:
                for key, value in __m:
                    convert_and_set(key, value)
        for key in kwargs:
            convert_and_set(key, kwargs[key])

    def to_json(
        self, filename=None, encoding="utf-8", errors="strict", **json_kwargs
    ):
        """
        Transform the DataDict object into a JSON string.

        :param filename: If provided will save to file
        :param encoding: File encoding
        :param errors: How to handle encoding errors
        :param json_kwargs: additional arguments to pass to json.dump(s)
        :return: string of JSON (if no filename provided)
        """
        from dynaconf.vendor.box.converters import _to_json

        return _to_json(
            self.to_dict(),
            filename=filename,
            encoding=encoding,
            errors=errors,
            **json_kwargs,
        )

    def to_yaml(
        self,
        filename=None,
        default_flow_style=False,
        encoding="utf-8",
        errors="strict",
        **yaml_kwargs,
    ):
        """
        Transform the DataDict object into a YAML string.

        :param filename:  If provided will save to file
        :param default_flow_style: False will recursively dump dicts
        :param encoding: File encoding
        :param errors: How to handle encoding errors
        :param yaml_kwargs: additional arguments to pass to yaml.dump
        :return: string of YAML (if no filename provided)
        """
        from dynaconf.vendor.box.converters import _to_yaml

        return _to_yaml(
            self.to_dict(),
            filename=filename,
            default_flow_style=default_flow_style,
            encoding=encoding,
            errors=errors,
            **yaml_kwargs,
        )

    def to_toml(self, filename=None, encoding="utf-8", errors="strict"):
        """
        Transform the DataDict object into a toml string.

        :param filename: File to write toml object too
        :param encoding: File encoding
        :param errors: How to handle encoding errors
        :return: string of TOML (if no filename provided)
        """
        from dynaconf.vendor.box.converters import _to_toml

        return _to_toml(
            self.to_dict(), filename=filename, encoding=encoding, errors=errors
        )

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
        """
        Turn the DataList and sub DataLists back into a native python list.

        :return: python list of this DataList
        """
        new_list = []
        for x in self:
            if x is self:
                new_list.append(new_list)
            elif isinstance(x, DataDict):
                new_list.append(x.to_dict())
            elif isinstance(x, DataList):
                new_list.append(x.to_list())
            else:
                new_list.append(x)
        return new_list

    def to_json(
        self,
        filename=None,
        encoding="utf-8",
        errors="strict",
        multiline=False,
        **json_kwargs,
    ):
        """
        Transform the DataList object into a JSON string.

        :param filename: If provided will save to file
        :param encoding: File encoding
        :param errors: How to handle encoding errors
        :param multiline: Put each item in list onto it's own line
        :param json_kwargs: additional arguments to pass to json.dump(s)
        :return: string of JSON or return of `json.dump`
        """
        from dynaconf.vendor.box.converters import _to_json

        if filename and multiline:
            lines = [
                _to_json(
                    item,
                    filename=False,
                    encoding=encoding,
                    errors=errors,
                    **json_kwargs,
                )
                for item in self
            ]
            with open(filename, "w", encoding=encoding, errors=errors) as f:
                f.write("\n".join(lines))
        else:
            return _to_json(
                self.to_list(),
                filename=filename,
                encoding=encoding,
                errors=errors,
                **json_kwargs,
            )

    def to_yaml(
        self,
        filename=None,
        default_flow_style=False,
        encoding="utf-8",
        errors="strict",
        **yaml_kwargs,
    ):
        """
        Transform the DataList object into a YAML string.

        :param filename:  If provided will save to file
        :param default_flow_style: False will recursively dump dicts
        :param encoding: File encoding
        :param errors: How to handle encoding errors
        :param yaml_kwargs: additional arguments to pass to yaml.dump
        :return: string of YAML or return of `yaml.dump`
        """
        from dynaconf.vendor.box.converters import _to_yaml

        return _to_yaml(
            self.to_list(),
            filename=filename,
            default_flow_style=default_flow_style,
            encoding=encoding,
            errors=errors,
            **yaml_kwargs,
        )

    def to_toml(
        self, filename=None, key_name="toml", encoding="utf-8", errors="strict"
    ):
        """
        Transform the DataList object into a toml string.

        :param filename: File to write toml object too
        :param key_name: Specify the name of the key to store the string under
            (cannot directly convert to toml)
        :param encoding: File encoding
        :param errors: How to handle encoding errors
        :return: string of TOML (if no filename provided)
        """
        from dynaconf.vendor.box.converters import _to_toml

        return _to_toml(
            {key_name: self.to_list()},
            filename=filename,
            encoding=encoding,
            errors=errors,
        )

    def to_csv(self, filename, encoding="utf-8", errors="strict"):
        """
        Transform the DataList object into a CSV file.

        :param filename: File to write CSV data to
        :param encoding: File encoding
        :param errors: How to handle encoding errors
        """
        from dynaconf.vendor.box.converters import _to_csv

        _to_csv(self, filename=filename, encoding=encoding, errors=errors)

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
    def from_csv(cls, filename, encoding="utf-8", errors="strict"):
        """
        Transform a CSV file into a DataList object.

        :param filename: CSV file to read from
        :param encoding: File encoding
        :param errors: How to handle encoding errors
        :return: DataList object from CSV data
        """
        from dynaconf.vendor.box.converters import _from_csv

        return cls(
            _from_csv(filename=filename, encoding=encoding, errors=errors)
        )


DataNode = Union[DataDict, DataList]
