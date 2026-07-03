"""Render: the ordered/condensed tenure -> final legal-description text.

Fills the category template and formats to the prescribed convention, including
area to AREA_DECIMALS and the "more or less" tail. Marks any provisional
(PMBC/PID-derived) portions loudly per the per-parcel flag so the user can see
which parts are not yet authoritative.
"""

from __future__ import annotations

from lds.engine.models import TenureDescription


def render(tenure: TenureDescription) -> str:
    """Produce the final legal-description text for the tenure.

    For refused tenures, returns a clear refusal/flag message rather than a
    best-effort description.
    """
    raise NotImplementedError("Phase 4: render final legal text from the condensed tenure")
