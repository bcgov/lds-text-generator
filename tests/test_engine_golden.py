"""Phase 4 — golden description fixtures.

Fixtures are produced in PHASE 2 by tools/capture_fixtures.py (real overlaps
paired with their Query_2 validated descriptions), then confirmed and tiered:

    descriptions/*.json          seeds (hand-built start-against examples)
    descriptions/core/*.json     confirmed real captures — MUST pass
    descriptions/stretch/*.json  harder cases — may xfail until handled

Each fixture's `expected_description` is the OWNER-APPROVED target text — at the
confirmation checkpoint the owner may normalize the raw historical wording to
current house style (the raw text stays in `source_description` for reference).
Byte-matching unedited historical text is NOT the success metric (docs/rules.md).

This test auto-discovers all fixtures. It already asserts, today, that every
fixture is schema-valid and carries a non-empty expectation — so fixture files
break loudly if the contract or the capture format drifts. The engine-equality
assertion is wired in Phase 4; until then it xfails.
"""

import pytest
from conftest import discover_description_fixtures

from lds.contracts.overlap import StructuredOverlap

FIXTURES = discover_description_fixtures("all")


@pytest.mark.skipif(not FIXTURES, reason="no golden description fixtures present yet")
@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda f: f"{f.get('_tier')}:{f.get('_name')}")
def test_engine_reproduces_expected_description(fixture):
    # Real assertions that hold from Phase 1: the fixture must be usable.
    overlap = StructuredOverlap.model_validate(fixture["overlap"])
    expected = fixture["expected_description"]
    assert expected and expected.strip(), "fixture has no expected description"
    assert overlap.tenure_id, "fixture overlap has no tenure id"

    # STRETCH fixtures are allowed to fail until the engine handles them.
    if fixture.get("_tier") == "stretch":
        pytest.xfail("stretch fixture: aspirational coverage")

    # Phase 4: wire the engine pipeline and assert equality. Until then, xfail.
    pytest.xfail("Phase 4: engine pipeline not implemented yet")

    # from lds.engine.classify import classify
    # from lds.engine.condense import condense
    # from lds.engine.ingest import ingest
    # from lds.engine.render import render
    # rendered = render(condense(classify(ingest(overlap))))
    # assert rendered == expected
