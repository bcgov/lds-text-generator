"""Phase 4 — deterministic parser on the catalogued hard forms.

See docs/parsing_complexity.md. The parser must never raise; it marks
unparseable strings unparsed. Failing placeholders define the targets.
"""

import pytest


@pytest.mark.skip(reason="Phase 4: parse abbreviated forms (PCL.F, RGES.5&6, ...)")
def test_parses_heavy_abbreviation():
    raise NotImplementedError


@pytest.mark.skip(reason="Phase 4: except-clauses captured")
def test_parses_except_clauses():
    raise NotImplementedError


@pytest.mark.skip(reason="Phase 4: unparseable string marked unparsed, not raised")
def test_unparseable_marked_not_raised():
    raise NotImplementedError
