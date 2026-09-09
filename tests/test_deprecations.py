from __future__ import annotations

import pytest

from dynaconf.utils.boxing import DynaBox


class TestDynaBoxDeprecation:
    def test_warns_on_instantiation(self):
        with pytest.warns(DeprecationWarning) as record:
            DynaBox()

        assert len(record) == 1
        msg = str(record[0].message)
        assert "DynaBox is deprecated" in msg
        assert "4.0.0" in msg
        assert "dynaconf.DataDict" in msg
