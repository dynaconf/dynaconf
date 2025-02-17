from __future__ import annotations

BANDS = ["Metallica", "Black Sabbath", "Iron Maiden"]


# This is really bad, however there are some running projects using it.
# namely pulp_ansible <0.24
from dynaconf import settings

# this must be avoided in favor of lazy format, get a and hooks
BAD = settings.BEST_BOSS + "/foo"
# the following is ok
GOOD = "@format {this.TEST_VALUE}/foo"
