"""Engine-internal data model.

These are the working types the engine passes between parse -> classify ->
condense -> render. They are distinct from the contract types (lds.contracts):
the contract is the external interchange; these are internal to the engine and may
evolve freely as long as ingest.py maps the contract into them.

Kept deliberately simple and explicit for readability.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class DescriptionCategory(StrEnum):
    """The 12 v1 description categories, per the instruction document
    (docs/instructions/commonplace_AI_legal_description_instructions.txt).
    ROW categories (13-21) are out of v1 and are represented as out-of-scope,
    not here. Templates per category are implemented in render.py (Phase 4).
    """

    SURVEY_PARCEL = "survey_parcel"                                # category 1
    PART_OF_SURVEY_PARCEL = "part_of_survey_parcel"                # category 2
    UNSURVEYED_UPLAND = "unsurveyed_upland"                        # category 3
    UNSURVEYED_FORESHORE = "unsurveyed_foreshore"                  # category 4
    SURVEYED_AND_UNSURVEYED_UPLAND = "surveyed_and_unsurveyed_upland"          # 5
    SURVEYED_AND_UNSURVEYED_FORESHORE = "surveyed_and_unsurveyed_foreshore"    # 6
    PART_SURVEYED_AND_UNSURVEYED_UPLAND = "part_surveyed_and_unsurveyed_upland"      # 7
    PART_SURVEYED_AND_UNSURVEYED_FORESHORE = "part_surveyed_and_unsurveyed_foreshore"  # 8
    SURVEY_PARCEL_IN_MINERAL_CLAIM = "survey_parcel_in_mineral_claim"          # 9
    SURVEY_PARCELS_IN_MULTIPLE_MINERAL_CLAIMS = "survey_parcels_in_multiple_mineral_claims"  # 10
    IN_LOT_WITH_MINERAL_CLAIM = "in_lot_with_mineral_claim"        # category 11
    PART_SURVEYED_MINERAL_CLAIM_AND_UNSURVEYED_UPLAND = (
        "part_surveyed_mineral_claim_and_unsurveyed_upland"        # category 12
    )


class RemainderKind(StrEnum):
    """Engine-side remainder classification (mirrors the contract's
    RemainderType; kept separate so the engine model can evolve freely)."""

    UPLAND = "upland"
    FORESHORE = "foreshore"


@dataclass
class Parcel:
    """A parcel as the engine sees it after ingest, ready to classify/condense."""

    legal_description: str
    land_district: str
    is_whole: bool
    is_district_lot: bool = False
    lot: str | None = None
    sublot: str | None = None
    block: str | None = None
    section: str | None = None
    township: str | None = None
    range: str | None = None
    plan: str | None = None
    exceptions: list[str] = field(default_factory=list)
    provisional: bool = False           # PMBC/PID fallback text (loud flag downstream)
    unparsed: bool = False              # parser could not parse -> flag, do not render
    sort_key: tuple = field(default_factory=tuple)  # filled by condense


@dataclass
class Remainder:
    """One unsurveyed remainder as the engine renders it.

    One record per land district (the contract guarantees per-district splitting),
    each with its own area, so the renderer can produce all three district-naming
    forms: single trailing district, per-group repeated districts, and the
    districts-listed-together unsurveyed-only clause. feature_name is the
    human-confirmed citation (from the selected CandidateFeature), never
    auto-picked.
    """

    kind: RemainderKind
    area_ha: float
    land_district: str | None = None
    feature_name: str | None = None   # confirmed vicinity feature / water body


@dataclass
class TenureDescription:
    """The engine's working representation of a tenure before rendering."""

    tenure_id: str
    category: DescriptionCategory | None = None
    parcels: list[Parcel] = field(default_factory=list)
    remainders: list[Remainder] = field(default_factory=list)
    land_districts: list[str] = field(default_factory=list)
    area_ha: float = 0.0
    is_refused: bool = False
    refusal_reasons: list[str] = field(default_factory=list)
    has_provisional_text: bool = False
