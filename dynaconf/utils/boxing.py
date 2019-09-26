from box import Box

from dynaconf.utils import upperfy


class DynaBox(Box):
    """Specialized Box for dynaconf
    it allows items/attrs to be found both in upper or lower case"""

    def __getattr__(self, item, *args, **kwargs):
        try:
            return super(DynaBox, self).__getattr__(item, *args, **kwargs)
        except (AttributeError, KeyError):
            n_item = item.lower() if item.isupper() else upperfy(item)
            return super(DynaBox, self).__getattr__(n_item, *args, **kwargs)

    def __getitem__(self, item, *args, **kwargs):
        try:
            return super(DynaBox, self).__getitem__(item, *args, **kwargs)
        except (AttributeError, KeyError):
            n_item = item.lower() if item.isupper() else upperfy(item)
            return super(DynaBox, self).__getitem__(n_item, *args, **kwargs)

    def __copy__(self):
        return self.__class__(super(Box, self).copy())

    def copy(self):
        return self.__class__(super(Box, self).copy())

    def get(self, item, default=None, *args, **kwargs):
        value = super(DynaBox, self).get(item, default, *args, **kwargs)
        if value is None or value == default:
            n_item = item.lower() if item.isupper() else upperfy(item)
            value = super(DynaBox, self).get(n_item, default, *args, **kwargs)
        return value
