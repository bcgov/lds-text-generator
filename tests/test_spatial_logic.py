"""Phase 2 — DB-independent spatial logic tests.

These target the PURE logic factored out of the SQL (whole/part, sliver rule, ROW
decision, decision-tree routing, contract conformance), so they run with no
database. They are written as failing placeholders that define what the Phase 2
implementation must satisfy. Fill them in as the logic lands.
"""

import pytest

from lds.constants import WHOLE_PART_THRESHOLD


@pytest.mark.skip(reason="Phase 2: implement whole/part classification helper")
def test_whole_part_boundary():
    # A parcel at exactly WHOLE_PART_THRESHOLD coverage is WHOLE; just below is PART.
    assert WHOLE_PART_THRESHOLD == 0.999  # guard the calibrated value
    raise NotImplementedError


@pytest.mark.skip(reason="Phase 2: implement sliver inclusion rule")
def test_sliver_inclusion_rule():
    # Include if intersection area >= MIN_AREA OR ratio >= MIN_RATIO; else exclude.
    raise NotImplementedError


@pytest.mark.skip(reason="Phase 2: ROW uses its own gate; flagged tenure still builds fully")
def test_row_meaningful_uses_dedicated_row_gate():
    # ROW_MEANINGFUL_* (not the sliver gate) decides the flag, and a flagged
    # tenure still produces a complete, reviewable overlap (is_refused=True).
    raise NotImplementedError


@pytest.mark.skip(reason="Phase 2: no-overlap decision tree routing")
def test_no_overlap_decision_tree_routes_pid_gap_foreshore_upland_grid_insufficient():
    # Given classified remainder inputs, assert the correct branch is taken.
    raise NotImplementedError


@pytest.mark.skip(reason="Phase 2: assembled output must be a valid StructuredOverlap")
def test_assembled_overlap_conforms_to_contract():
    raise NotImplementedError
