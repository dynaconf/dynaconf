# coding: utf-8

from box import Box


class DynaBox(Box):
    """Specialized Box for dynaconf
    it allows items/attrs to be founf both in upper or lower case"""

    def __getattr__(self, item):
        try:
            return super(DynaBox, self).__getattr__(item)
        except (AttributeError, KeyError):
            n_item = item.lower() if item.isupper() else item.upper()
            return super(DynaBox, self).__getattr__(n_item)

    def __getitem__(self, item):
        try:
            return super(DynaBox, self).__getitem__(item)
        except (AttributeError, KeyError):
            n_item = item.lower() if item.isupper() else item.upper()
            return super(DynaBox, self).__getitem__(n_item)

    def get(self, item, default=None):
        value = super(DynaBox, self).get(item, default)
        if value is None or value == default:
            n_item = item.lower() if item.isupper() else item.upper()
            value = super(DynaBox, self).get(n_item, default)
        return value
