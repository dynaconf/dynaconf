def get_annotations(schema_cls) -> dict:
    """NOTE: move to inspect.get_annotations when Python 3.9 is dropped"""
    if isinstance(schema_cls, type):
        return schema_cls.__dict__.get("__annotations__", {})
    else:
        return getattr(schema_cls, "__annotations__", {})
