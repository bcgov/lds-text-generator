"""Phase 4 — category selection and out-of-scope refusal."""

import pytest


@pytest.mark.skip(reason="Phase 4: clear category for surveyed/unsurveyed cases")
def test_category_for_clear_cases():
    raise NotImplementedError


@pytest.mark.skip(reason="Phase 4: ROW / grid-only inputs are refused, not mis-generated")
def test_out_of_scope_refused():
    raise NotImplementedError
