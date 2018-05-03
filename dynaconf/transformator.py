# coding: utf-8
# pragma: no cover


class Transformator:
    """Rule to transform values"""
    def __init__(self, *args, **kwargs):
        pass


class TransformatorList(list):
    """Wrapper for all registered Transformators"""
    def __init__(self, settings, *args, **kwargs):
        super(TransformatorList, self).__init__(*args, **kwargs)
        self.settings = settings

    def register(self, *args):
        self.extend(args)
