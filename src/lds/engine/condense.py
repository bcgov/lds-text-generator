"""Condense: order and group parcels to the registry convention.

Sort key (data-derived; project plan, the dominant convention, not byte-matching
historical text):
  1. within-tenure (whole) parcels before partial parcels;
  2. subdivision units (Lot/Sublot/Block) before their containing District Lot;
  3. ascending by number within type.

Then group/condense: collapse runs, apply "those parts of" vs "that part of",
pluralize, propagate except-clauses, and handle the multi-district structure
(single district stated once; multi-district-with-parcels repeats the district per
group; multi-district-unsurveyed lists districts together).
"""

from __future__ import annotations

from lds.engine.models import TenureDescription


def condense(tenure: TenureDescription) -> TenureDescription:
    """Apply the sort order and grouping/condensing rules. Returns the tenure with
    parcels ordered and sort_keys assigned, ready to render."""
    raise NotImplementedError("Phase 4: sort + group + condense")
