from __future__ import annotations


class DummyExtensionType:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if not hasattr(app, "extensions"):
            app.extensions = {}
        app.extensions["dummy"] = self


dummy_instance = DummyExtensionType()
