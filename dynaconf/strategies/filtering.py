from dynaconf.utils import upperfy


class PrefixFilter:

    def __init__(self, prefix):
        if not isinstance(prefix, str):
            raise TypeError("`SETTINGS_FILE_PREFIX` must be str")
        self.prefix = "{}_".format(upperfy(prefix))

    def __call__(self, data):
        """Filter incoming data by prefix"""
        prefix = self.prefix
        return {
                upperfy(
                    k[len(prefix):]
                ): v for k, v in data.items()
                if upperfy(k[:len(prefix)]) == prefix
         }
