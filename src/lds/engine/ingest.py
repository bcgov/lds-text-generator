"""Ingest: map a StructuredOverlap (the contract) into the engine's working model.

This is the only place the engine touches the contract types. Everything
downstream (classify/condense/render/validate) operates on engine.models. Keeping
the mapping in one module is what preserves the clean boundary: the contract can
change shape and only ingest.py needs to follow.
"""

from __future__ import annotations

from lds.contracts.overlap import StructuredOverlap
from lds.engine.models import TenureDescription


def ingest(overlap: StructuredOverlap) -> TenureDescription:
    """Convert a StructuredOverlap into a TenureDescription for the engine.

    Carries across: parcels (with whole/part and provisional flags), unsurveyed
    remainders (as vicinity features / foreshore water body), land districts, area,
    and any refusal conditions from out_of_scope_flags. PID-gap parcels arrive as
    provisional parcels (their fallback text is already in source_legal_description).
    """
    raise NotImplementedError("Phase 4: map contract -> engine model")
