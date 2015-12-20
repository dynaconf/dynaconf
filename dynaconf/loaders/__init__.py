from dynaconf import default_settings


def default_loader(obj):
    for key, value in default_settings.__dict__.items():
        if key.isupper():
            setattr(obj, key, value)
