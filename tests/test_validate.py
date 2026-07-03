"""Phase 4 — validation: contract comparison (Layer 1) + round-trip/lints (Layer 2)."""

import pytest


@pytest.mark.skip(reason="Phase 4: round-trip catches a corrupted render")
def test_roundtrip_catches_corruption():
    raise NotImplementedError


@pytest.mark.skip(reason="Phase 4: district lint follows single/multi rule, not 'named once'")
def test_district_lint_single_multi_rule():
    raise NotImplementedError


@pytest.mark.skip(reason="Phase 4: contract comparison catches a dropped parcel")
def test_contract_comparison_catches_dropped_parcel():
    raise NotImplementedError
