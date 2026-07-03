"""Workbook import: a spreadsheet overlap -> StructuredOverlap. Phase 6.

The contract has two producers: the live spatial stage, and an imported workbook
(the spreadsheet format used in the manual process today — one sheet per tenure,
columns OVERLAP_LEGAL_DESCRIPTION / WITHIN_Y_N / AREA_HA and, for unsurveyed
land, PHYSICAL_FEATURE / UNSURVEYED_LAND_DISTRICT). Real examples of the format
are committed: tests/fixtures/discovery/multi_shape.xlsx (9 sheets, minimal
columns) and complex_shape.xlsx (full column set). This module is the second
producer: it lets a tenure that never went through the spatial stage still be
described and validated.

Neutral placement (not spatial/, not engine/): it depends only on the contract
and openpyxl. Workbook-sourced overlaps carry source_type=WORKBOOK so the engine
knows the record was not produced by the live overlay (classify guards
independently for exactly this case).
"""

from __future__ import annotations

from pathlib import Path

from lds.contracts.overlap import StructuredOverlap


def load_overlap_from_workbook(path: Path, tenure_id: str) -> StructuredOverlap:
    """Read one tenure's sheet from a workbook and build a StructuredOverlap.

    The sheet supplies less than the live overlay does (no coverage ratios, no
    PMBC detection, no candidate features) — populate what it has, set
    source_type=WORKBOOK, and record the gaps as validation messages so the
    reviewer sees what the record is missing.
    """
    raise NotImplementedError("Phase 6: map the workbook sheet onto the contract")
