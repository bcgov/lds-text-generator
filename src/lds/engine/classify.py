"""Classify: choose the description category (1-12) or refuse (out of v1 scope).

Selects the DescriptionCategory from the ingested tenure, OR determines that the
tenure is out of v1 scope and must be refused (ROW phrasing families, grid-only
references, deferred categories 13-21). Refusal is first-class: never mis-generate
for an input the engine cannot map to a category.

Detection here is the engine-side guard; the spatial stage also flags early, but
the engine must guard independently because it can be fed an imported workbook that
never went through the spatial stage.
"""

from __future__ import annotations

from lds.engine.models import TenureDescription


def classify(tenure: TenureDescription) -> TenureDescription:
    """Set tenure.category, or mark tenure.is_refused with reasons.

    Returns the same tenure with classification applied.
    """
    raise NotImplementedError("Phase 4: category selection + out-of-scope refusal")
