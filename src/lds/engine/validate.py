"""Validate: check the generated description.

Two layers (project plan section 9):

Layer 1 - compare against the structured overlap (the input contract), which is
independent of the renderer:
  - generated component set matches the overlap's component set;
  - independent parcel-count check;
  - independent whole/part-count check;
  - every land district validated against the authoritative gazetteer;
  - low parser confidence raises a warning.

Layer 2 - round-trip and deterministic lints:
  - re-parse the generated text and assert the parcel set matches;
  - district naming conforms to the single/multi-district rule (NOT "named once");
  - "together with" placement; except-clause propagation; template conformance.

Round-trip is necessary but NOT sufficient (parser+renderer can share a wrong
assumption), which is why Layer 1 compares against the contract independently.
"""

from __future__ import annotations

from lds.contracts.overlap import StructuredOverlap, ValidationMessage
from lds.engine.models import TenureDescription


def validate(
    rendered_text: str,
    tenure: TenureDescription,
    overlap: StructuredOverlap,
) -> list[ValidationMessage]:
    """Run both validation layers and return any messages (info/warning/error)."""
    raise NotImplementedError("Phase 4: contract-comparison + round-trip + lints")
