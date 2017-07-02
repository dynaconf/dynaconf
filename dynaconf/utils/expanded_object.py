class ExpandedObject:
    def __init__(self, **data):
        for key, value in data.items():
            key = key.strip().upper()
            if isinstance(value, dict):
                self.__dict__[key] = ExpandedObject(**value)
            else:
                self.__dict__[key] = value
