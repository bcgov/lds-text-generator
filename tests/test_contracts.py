"""Contract tests (Phase 1) — real assertions on the structured-overlap schema.

These should PASS as soon as the contract module is in place. They define the
behaviour the rest of the codebase relies on.
"""

from __future__ import annotations

import json

import pydantic
import pytest
from conftest import (
    ALL_SAMPLES,
    OVERLAYS_DIR,
    sample_multi_district,
    sample_single_district,
    sample_with_pid_gap,
    sample_with_unsurveyed_remainder,
)

from lds.contracts.overlap import (
    OverlapParcel,
    ParcelType,
    StructuredOverlap,
    TextSource,
    WholePart,
)


def _valid_parcel_kwargs() -> dict:
    """A minimal valid OverlapParcel, for the invariant tests to corrupt."""
    return dict(
        source_legal_description="District Lot 1, Testville District",
        parcel_type=ParcelType.PRIMARY,
        land_district="Testville District",
        overlap_area_ha=1.0,
        parcel_area_ha=2.0,
        coverage_ratio=0.5,
        whole_part_flag=WholePart.PART,
    )


def test_single_district_builds_and_roundtrips():
    overlap = sample_single_district()
    dumped = overlap.model_dump_json()
    restored = StructuredOverlap.model_validate(json.loads(dumped))
    assert restored == overlap


def test_serialized_overlay_fixtures_load():
    # The four sample shapes are also committed as JSON files; loading them
    # freezes the serialization shape against accidental contract changes.
    paths = sorted(OVERLAYS_DIR.glob("*.json"))
    assert len(paths) == 4, f"expected 4 overlay fixture files in {OVERLAYS_DIR}"
    for path in paths:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        restored = StructuredOverlap.model_validate(data)
        rebuilt = ALL_SAMPLES[path.stem]()
        assert restored == rebuilt, f"{path.name} no longer matches its factory"


def test_predicates_on_single_district():
    overlap = sample_single_district()
    assert overlap.is_multi_district is False
    assert overlap.land_districts == ["Similkameen Division Yale District"]
    assert overlap.has_provisional_text is False
    assert overlap.is_refused is False


def test_multi_district_detected():
    overlap = sample_multi_district()
    assert overlap.is_multi_district is True
    assert set(overlap.land_districts) == {"Seymour District", "Chemainus District"}


def test_remainder_districts_count_toward_land_districts():
    # An unsurveyed-only tenure has districts only on its remainders; the
    # single/multi wording rules depend on them, so the predicates must see them.
    overlap = sample_with_unsurveyed_remainder()
    assert overlap.land_districts == ["Kamloops Division Yale District"]
    assert overlap.is_multi_district is False


def test_whole_and_part_flags_present():
    overlap = sample_single_district()
    flags = {p.whole_part_flag for p in overlap.parcels}
    assert WholePart.WHOLE in flags
    assert WholePart.PART in flags


def test_unsurveyed_remainder_has_typed_candidates():
    overlap = sample_with_unsurveyed_remainder()
    assert len(overlap.unsurveyed_remainders) == 1
    rem = overlap.unsurveyed_remainders[0]
    assert rem.candidate_features, "remainder should carry candidate features"
    # candidates are proposed, never pre-selected
    assert all(c.selected is False for c in rem.candidate_features)


def test_pid_gap_has_provisional_parcel_and_maintenance_flag():
    overlap = sample_with_pid_gap()
    assert overlap.has_provisional_text is True
    provisional = [p for p in overlap.parcels if p.provisional]
    assert len(provisional) == 1
    assert provisional[0].text_source is TextSource.PMBC_PID_FALLBACK
    assert provisional[0].pid is not None
    # a PMBC-fallback parcel has no Tantalis record, hence no parcel type
    assert provisional[0].parcel_type is None
    # the gap is flagged for data maintenance, but does NOT make the tenure refused
    assert len(overlap.data_maintenance_flags) == 1
    assert overlap.is_refused is False


def test_coverage_ratio_bounds_enforced():
    kwargs = _valid_parcel_kwargs()
    kwargs.update(overlap_area_ha=2.0, parcel_area_ha=1.0, coverage_ratio=2.0)
    with pytest.raises(pydantic.ValidationError):
        OverlapParcel(**kwargs)


def test_provisional_must_match_text_source():
    # provisional=True with authoritative Tantalis text is contradictory
    kwargs = _valid_parcel_kwargs()
    kwargs.update(provisional=True)
    with pytest.raises(pydantic.ValidationError):
        OverlapParcel(**kwargs)
    # ...and PMBC fallback text without the provisional flag is too
    kwargs = _valid_parcel_kwargs()
    kwargs.update(text_source=TextSource.PMBC_PID_FALLBACK, pid="PID-1")
    with pytest.raises(pydantic.ValidationError):
        OverlapParcel(**kwargs)


def test_pmbc_fallback_requires_pid():
    kwargs = _valid_parcel_kwargs()
    kwargs.update(text_source=TextSource.PMBC_PID_FALLBACK, provisional=True, pid=None)
    with pytest.raises(pydantic.ValidationError):
        OverlapParcel(**kwargs)


def test_inconsistent_coverage_ratio_rejected():
    # ratio wildly different from overlap/parcel means rows were mixed up
    kwargs = _valid_parcel_kwargs()
    kwargs.update(coverage_ratio=0.9)  # true ratio is 0.5
    with pytest.raises(pydantic.ValidationError):
        OverlapParcel(**kwargs)
