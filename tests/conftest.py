"""Shared test fixtures and helpers.

Provides hand-built StructuredOverlap samples for the contract/engine tests, and an
auto-discovery helper so the project owner can drop their full validated
input/output fixtures into tests/fixtures/ and have them picked up automatically.

Also implements the `bcgw` marker contract: integration tests marked bcgw are
skipped automatically unless BCGW_USER / BCGW_PASSWORD / BCGW_DSN are set.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from lds.contracts.overlap import (
    CandidateFeature,
    DataMaintenanceFlag,
    DetectionSignal,
    FeatureSourceDataset,
    OverlapParcel,
    ParcelType,
    RemainderType,
    SourceType,
    StructuredOverlap,
    TextSource,
    UnsurveyedRemainder,
    WholePart,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"
OVERLAYS_DIR = FIXTURES_DIR / "overlays"
DESCRIPTIONS_DIR = FIXTURES_DIR / "descriptions"

BCGW_ENV_VARS = ("BCGW_USER", "BCGW_PASSWORD", "BCGW_DSN")


def pytest_collection_modifyitems(config, items):
    """Skip bcgw-marked integration tests when credentials are not configured."""
    if all(os.environ.get(var) for var in BCGW_ENV_VARS):
        return
    skip_bcgw = pytest.mark.skip(
        reason="BCGW credentials not set (BCGW_USER / BCGW_PASSWORD / BCGW_DSN)"
    )
    for item in items:
        if "bcgw" in item.keywords:
            item.add_marker(skip_bcgw)


# --- hand-built sample overlaps ---------------------------------------------
# These are also serialized under tests/fixtures/overlays/ (see
# test_contracts.py), which freezes the JSON shape: a contract change that
# alters serialization fails the file-loading test.


def sample_single_district() -> StructuredOverlap:
    """A clean single-district tenure: one whole District Lot plus parts of others.
    Mirrors the canonical DL 526S example."""
    return StructuredOverlap(
        tenure_id="SAMPLE-SINGLE",
        source_type=SourceType.INTRID_SID,
        tenure_area_ha=202.53,
        area_method="TENURE_AREA_IN_HECTARES (Tantalis attribute)",
        oracle_sdo_tolerance=0.005,
        parcels=[
            OverlapParcel(
                source_legal_description="District Lot 526S",
                parcel_type=ParcelType.PRIMARY,
                land_district="Similkameen Division Yale District",
                overlap_area_ha=50.0,
                parcel_area_ha=50.0,
                coverage_ratio=1.0,
                whole_part_flag=WholePart.WHOLE,
                text_source=TextSource.TANTALIS_PIN,
                pin="PIN-526S",
            ),
            OverlapParcel(
                source_legal_description="District Lot 525S",
                parcel_type=ParcelType.PRIMARY,
                land_district="Similkameen Division Yale District",
                overlap_area_ha=20.0,
                parcel_area_ha=80.0,
                coverage_ratio=0.25,
                whole_part_flag=WholePart.PART,
                text_source=TextSource.TANTALIS_PIN,
                pin="PIN-525S",
            ),
        ],
    )


def sample_multi_district() -> StructuredOverlap:
    """A tenure spanning two districts with parcels in each (district repeats)."""
    return StructuredOverlap(
        tenure_id="SAMPLE-MULTI",
        source_type=SourceType.INTRID_SID,
        tenure_area_ha=120.0,
        area_method="TENURE_AREA_IN_HECTARES (Tantalis attribute)",
        parcels=[
            OverlapParcel(
                source_legal_description="Section 5, Range 7, Seymour District",
                parcel_type=ParcelType.PRIMARY,
                land_district="Seymour District",
                overlap_area_ha=60.0,
                parcel_area_ha=60.0,
                coverage_ratio=1.0,
                whole_part_flag=WholePart.WHOLE,
            ),
            OverlapParcel(
                source_legal_description="District Lot 67E&N, Chemainus District",
                parcel_type=ParcelType.PRIMARY,
                land_district="Chemainus District",
                overlap_area_ha=60.0,
                parcel_area_ha=60.0,
                coverage_ratio=1.0,
                whole_part_flag=WholePart.WHOLE,
            ),
        ],
    )


def sample_with_unsurveyed_remainder() -> StructuredOverlap:
    """A tenure with an unsurveyed upland remainder citing a nearby mountain."""
    return StructuredOverlap(
        tenure_id="SAMPLE-UNSURVEYED",
        source_type=SourceType.SUBMITTED_GEOMETRY,
        tenure_area_ha=0.0225,
        area_method="SDO_GEOM.SDO_AREA, EPSG:3005",
        unsurveyed_remainders=[
            UnsurveyedRemainder(
                area_ha=0.0225,
                land_district="Kamloops Division Yale District",
                remainder_type=RemainderType.UPLAND,
                candidate_features=[
                    CandidateFeature(
                        name="South Forge Mountain",
                        feature_type="Mountain",
                        distance_m=120.0,
                        source_dataset=FeatureSourceDataset.GNS_GEOGRAPHICAL_NAMES,
                    )
                ],
            )
        ],
    )


def sample_with_pid_gap() -> StructuredOverlap:
    """A tenure mostly clean Tantalis parcels plus a PID-gap portion: a provisional
    PMBC-fallback parcel AND a data-maintenance flag."""
    return StructuredOverlap(
        tenure_id="SAMPLE-PIDGAP",
        source_type=SourceType.INTRID_SID,
        tenure_area_ha=10.0,
        area_method="TENURE_AREA_IN_HECTARES (Tantalis attribute)",
        parcels=[
            OverlapParcel(
                source_legal_description="District Lot 100, Lillooet District",
                parcel_type=ParcelType.PRIMARY,
                land_district="Lillooet District",
                overlap_area_ha=9.0,
                parcel_area_ha=9.0,
                coverage_ratio=1.0,
                whole_part_flag=WholePart.WHOLE,
                text_source=TextSource.TANTALIS_PIN,
                pin="PIN-100",
            ),
            OverlapParcel(
                # PMBC/LTSA fallback text; no Tantalis record, so no parcel_type.
                source_legal_description="Lot 5, Plan 1234, Lillooet District",
                parcel_type=None,
                land_district="Lillooet District",
                overlap_area_ha=1.0,
                parcel_area_ha=1.0,
                coverage_ratio=1.0,
                whole_part_flag=WholePart.WHOLE,
                text_source=TextSource.PMBC_PID_FALLBACK,
                provisional=True,
                pid="PID-000-111-222",
                flags=["PID-derived, provisional pending Tantalis survey parcel"],
            ),
        ],
        data_maintenance_flags=[
            DataMaintenanceFlag(
                pid="PID-000-111-222",
                area_ha=1.0,
                detected_by=DetectionSignal.REMAINDER_OVERLAY,
            )
        ],
    )


ALL_SAMPLES = {
    "single_district": sample_single_district,
    "multi_district": sample_multi_district,
    "with_unsurveyed_remainder": sample_with_unsurveyed_remainder,
    "with_pid_gap": sample_with_pid_gap,
}


# --- golden fixture discovery -----------------------------------------------


def discover_description_fixtures(tier: str = "all") -> list[dict]:
    """Load golden input/output fixtures from tests/fixtures/descriptions/.

    Layout (produced in Phase 2 by tools/capture_fixtures.py, see the plan):
        descriptions/*.json          -> hand-built seeds (start-against examples)
        descriptions/core/*.json     -> confirmed real captures (MUST pass)
        descriptions/stretch/*.json  -> harder cases (may xfail until handled)

    Each fixture is JSON with:
        overlap               -> StructuredOverlap dict (the engine input)
        expected_description  -> the OWNER-APPROVED target text the engine must
                                 produce (may be normalized to house style at the
                                 confirmation checkpoint)
        source_description    -> optional: the raw historical LEGAL_DESC the pair
                                 was captured against, kept verbatim for reference
        intrid_sid, captured_at -> optional capture provenance

    `_name` and `_tier` keys are added so the test can report and tier them.

    Args:
        tier: 'all', 'core', 'stretch', or 'seed' to filter what is returned.
    """
    fixtures: list[dict] = []
    if not DESCRIPTIONS_DIR.exists():
        return fixtures

    def _load(path: Path, tier_name: str) -> dict:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        data["_name"] = path.stem
        data["_tier"] = tier_name
        return data

    if tier in ("all", "seed"):
        for path in sorted(DESCRIPTIONS_DIR.glob("*.json")):
            fixtures.append(_load(path, "seed"))
    if tier in ("all", "core"):
        for path in sorted((DESCRIPTIONS_DIR / "core").glob("*.json")):
            fixtures.append(_load(path, "core"))
    if tier in ("all", "stretch"):
        for path in sorted((DESCRIPTIONS_DIR / "stretch").glob("*.json")):
            fixtures.append(_load(path, "stretch"))
    return fixtures
