"""Structured-overlap contract.

This module defines the interchange record that connects the two stages of the
tool. It is the single most important shared artifact in the codebase:

    spatial stage  ->  StructuredOverlap  ->  text engine

The spatial stage (Oracle + GeoPandas) produces a StructuredOverlap. The text
engine consumes it. Neither stage imports the other; both depend only on this
module. Keeping this contract clean and stable is what lets the two stages be
built, tested, and deployed independently.

The record is also an inspectable intermediate: it can be exported, reviewed and
corrected by a person at the review checkpoint, or passed straight through.

Design notes:
- The parcels list holds the parcels that will appear in the description. A parcel
  may be sourced from Tantalis (the normal case) or, for a PID-gap portion, from
  PMBC as flagged provisional fallback text (see TextSource / provisional below).
  The provisional/text_source pairing is an enforced invariant, not a convention.
- Excluded parcels do not silently vanish: anything that triggered a refusal,
  a flag, or a data-maintenance action is recorded in the relevant list.
- candidate_features is always a list of typed candidates; the spatial stage never
  auto-selects the feature cited in a vicinity description.
- An unsurveyed remainder record covers ONE land district. A remainder that spans
  several districts is split by the spatial stage into one record per district,
  so the engine can apply the multi-district wording rules (see docs/rules.md).
- The record carries provenance (schema_version, generated_at, generator_version,
  source_type, area_method, oracle_sdo_tolerance, per-parcel text_source /
  confidence) so a generated description is traceable, which matters for legal
  output.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

# Bump when the shape of the record changes, so serialized overlaps (exports,
# golden fixtures) can be told apart from a newer schema.
SCHEMA_VERSION = "1.0"

# How far coverage_ratio may disagree with overlap_area_ha / parcel_area_ha
# before the record is rejected as internally inconsistent. Loose enough for
# rounded inputs, tight enough to catch assembly bugs (e.g. mismatched rows).
_RATIO_CONSISTENCY_TOLERANCE = 0.01


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class SourceType(StrEnum):
    """How the tenure geometry entered the pipeline."""

    INTRID_SID = "intrid_sid"          # looked up in BCGW by Tantalis parcel id
    SUBMITTED_GEOMETRY = "submitted_geometry"  # uploaded shp/gdb/kml/geojson/...
    WORKBOOK = "workbook"              # imported structured overlap (no spatial run)


class ParcelType(StrEnum):
    """Tantalis survey-parcel type. Inclusion rule: keep PRIMARY and SUBDIVISION;
    RIGHT_OF_WAY is the only excluded type (assessed before exclusion, see
    docs/PROJECT_PLAN.md section 8a). Title is not an input to inclusion."""

    PRIMARY = "Primary"
    SUBDIVISION = "Subdivision"
    RIGHT_OF_WAY = "Right-of-Way"


class WholePart(StrEnum):
    """Whether the tenure covers the whole parcel or only part of it.
    Determined by coverage_ratio >= WHOLE_PART_THRESHOLD (see constants)."""

    WHOLE = "whole"
    PART = "part"


class TextSource(StrEnum):
    """Where a parcel's legal-description text came from.

    TANTALIS_PIN is authoritative. PMBC_PID_FALLBACK is provisional text generated
    for a PID-gap portion (a titled PMBC parcel missing from the Tantalis fabric);
    it must be regenerated from the PIN once the survey parcel exists.
    """

    TANTALIS_PIN = "tantalis_pin"
    PMBC_PID_FALLBACK = "pmbc_pid_fallback"


class RemainderType(StrEnum):
    """Classification of a piece of tenure not covered by any Tantalis parcel."""

    UPLAND = "upland"          # unsurveyed upland -> "in the vicinity of [feature]"
    FORESHORE = "foreshore"    # unsurveyed foreshore -> "bed of [water body]"
    UNKNOWN = "unknown"        # could not classify -> refuse / manual review


class FeatureSourceDataset(StrEnum):
    """Which dataset a named-feature candidate came from."""

    FWA_BAYS_AND_CHANNELS = "FWA_BAYS_AND_CHANNELS_POLY"
    FWA_STREAM_NETWORKS = "FWA_STREAM_NETWORKS_SP"
    FWA_LAKES = "FWA_LAKES_POLY"
    GNS_GEOGRAPHICAL_NAMES = "GNS_GEOGRAPHICAL_NAMES_SP"


class OutOfScopeReason(StrEnum):
    """Why a tenure (or part of it) was flagged out of v1 scope."""

    ROW_OVERLAP = "row_overlap"                  # meaningful Right-of-Way overlap
    GRID_ONLY = "grid_only"                      # NTS/PNG grid reference only
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"  # remainder resolves to nothing
    CATEGORY_13_TO_21 = "category_13_to_21"      # a deferred ROW description category


class DetectionSignal(StrEnum):
    """Which PMBC detection signal found a PID-gap (docs/PROJECT_PLAN.md 5.3b)."""

    REMAINDER_OVERLAY = "remainder_overlay"      # signal 1: remainder x PMBC (main)
    NULL_PID_HEURISTIC = "null_pid_heuristic"    # signal 2: null title id (secondary)


class MessageLevel(StrEnum):
    """Severity of a validation message."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


# ---------------------------------------------------------------------------
# Leaf records
# ---------------------------------------------------------------------------


class ParsedComponents(BaseModel):
    """Structured breakdown of a parcel's legal-description string.

    Produced by the engine's parser from source_legal_description. Fields are
    optional because not every descriptor is present in every parcel. This is the
    structured form the renderer and the condenser operate on.
    """

    lot: str | None = Field(None, description="Lot / District Lot identifier, e.g. '526S'")
    is_district_lot: bool = Field(False, description="True if the lot is a District Lot")
    sublot: str | None = Field(None, description="Sublot identifier if present")
    block: str | None = Field(None, description="Block identifier if present")
    section: str | None = Field(None, description="Section identifier if present")
    township: str | None = Field(None, description="Township if present")
    range: str | None = Field(None, description="Range if present")
    land_district: str | None = Field(None, description="Land district name")
    plan: str | None = Field(None, description="Survey plan number if present")
    exceptions: list[str] = Field(
        default_factory=list,
        description="Except-clauses, e.g. ['Plan 11544', 'that part now road on Plan H16902']",
    )
    raw: str | None = Field(
        None, description="The original string this was parsed from (for round-trip checks)"
    )
    unparsed: bool = Field(
        False,
        description="True if the parser could not confidently parse the string; "
        "the row is then flagged for manual entry rather than rendered.",
    )


class OverlapParcel(BaseModel):
    """A single parcel the tenure intersects, with the overlap measurements and
    provenance needed to render and validate its portion of the description."""

    source_legal_description: str = Field(
        ..., description="The parcel's legal-description text as held in the source fabric"
    )
    parsed_components: ParsedComponents | None = Field(
        None, description="Structured breakdown; populated by the engine's parser"
    )
    parcel_type: ParcelType | None = Field(
        None,
        description="Tantalis survey-parcel type. None for a PMBC-fallback parcel: "
        "a PID-gap portion has no Tantalis record and therefore no PARCEL_TYPE.",
    )
    land_district: str = Field(
        ...,
        description="Land district name. PMBC parcels carry no district attribute; "
        "the spatial stage derives it by spatial join against the districts view.",
    )

    overlap_area_ha: float = Field(..., ge=0, description="Area of tenure-parcel intersection")
    parcel_area_ha: float = Field(..., gt=0, description="Total area of the parcel")
    coverage_ratio: float = Field(
        ...,
        ge=0,
        le=1.0,
        description="overlap_area_ha / parcel_area_ha. The spatial stage CLAMPS "
        "tolerance noise (ratios slightly above 1) to 1.0 before assembly.",
    )
    whole_part_flag: WholePart

    text_source: TextSource = Field(
        TextSource.TANTALIS_PIN,
        description="Authoritative Tantalis text, or provisional PMBC/PID fallback",
    )
    provisional: bool = Field(
        False,
        description="True iff text_source is PMBC_PID_FALLBACK; the portion is "
        "PID-derived and must be regenerated from the PIN once available. Enforced.",
    )
    pin: str | None = Field(None, description="Tantalis survey-parcel id (PIN), when known")
    pid: str | None = Field(
        None, description="PMBC title id (PID); required when text_source is PMBC_PID_FALLBACK"
    )

    confidence: float | None = Field(
        None, ge=0, le=1, description="Parser confidence for this row, if parsed"
    )
    flags: list[str] = Field(
        default_factory=list,
        description="Per-parcel notes: low-confidence, PID-derived, repaired-geometry, etc.",
    )

    @model_validator(mode="after")
    def _check_invariants(self) -> OverlapParcel:
        # provisional and PMBC fallback are two views of one fact; never let them
        # disagree, or downstream flags/renders would contradict each other.
        is_fallback = self.text_source == TextSource.PMBC_PID_FALLBACK
        if self.provisional != is_fallback:
            raise ValueError(
                "provisional must be True exactly when text_source is PMBC_PID_FALLBACK "
                f"(got provisional={self.provisional}, text_source={self.text_source})"
            )
        if is_fallback and not self.pid:
            raise ValueError("a PMBC-fallback parcel must carry its PID")
        # The ratio is stored alongside the two areas it is derived from; a gross
        # disagreement means rows were mixed up during assembly.
        derived = self.overlap_area_ha / self.parcel_area_ha
        if abs(derived - self.coverage_ratio) > _RATIO_CONSISTENCY_TOLERANCE:
            raise ValueError(
                f"coverage_ratio {self.coverage_ratio} does not match "
                f"overlap_area_ha/parcel_area_ha = {derived:.6f}"
            )
        return self


class CandidateFeature(BaseModel):
    """A typed nearest-feature candidate for a vicinity / foreshore clause.

    The spatial stage returns these for human confirmation; it never auto-selects.
    """

    name: str = Field(..., description="The feature's name, e.g. 'Stoyama Mountain'")
    feature_type: str = Field(
        ..., description="The feature type, e.g. 'Mountain', 'Lake', 'Stream'"
    )
    distance_m: float = Field(..., ge=0, description="Distance from the remainder to the feature")
    source_dataset: FeatureSourceDataset
    selected: bool = Field(
        False, description="Set true once a person confirms this candidate at the checkpoint"
    )


class UnsurveyedRemainder(BaseModel):
    """A portion of the tenure not covered by any Tantalis survey parcel.

    Notes:
    - A remainder is NOT automatically out of scope. It is classified
      (upland / foreshore / unknown) and, for upland/foreshore, becomes a valid
      unsurveyed-land description.
    - One record covers ONE land district. The spatial stage splits a remainder
      that spans several districts into per-district records (with per-district
      areas), so the engine can apply the multi-district wording rules.
    - A remainder that is actually a PID-gap (a titled PMBC parcel missing from
      Tantalis) is handled separately and recorded as a DataMaintenanceFlag plus
      a provisional PMBC-fallback parcel, not here.
    """

    area_ha: float = Field(..., ge=0)
    land_district: str | None = None
    remainder_type: RemainderType
    candidate_features: list[CandidateFeature] = Field(default_factory=list)


class OutOfScopeFlag(BaseModel):
    """A reason the tenure (or part of it) cannot be handled in v1, with evidence."""

    reason: OutOfScopeReason
    detail: str = Field(..., description="Human-readable explanation and the evidence")
    area_ha: float | None = Field(None, description="Affected area, where applicable")


class DataMaintenanceFlag(BaseModel):
    """A PID-gap portion: a titled PMBC parcel present where the Tantalis survey
    parcel is missing. The portion still gets provisional PMBC-fallback text (see
    OverlapParcel.text_source), but is flagged here so the survey parcel can be
    created in Tantalis and the description regenerated from the PIN."""

    pid: str = Field(..., description="The PMBC title id present in the gap")
    area_ha: float = Field(..., ge=0)
    detected_by: DetectionSignal
    note: str = Field(
        "Provisional PMBC/PID text used; regenerate from PIN once the survey parcel exists.",
        description="Standing instruction for the maintenance action",
    )


class ValidationMessage(BaseModel):
    """A lint or check raised while assembling or validating the overlap/description."""

    level: MessageLevel
    code: str = Field(..., description="Stable machine code, e.g. 'district_vocab'")
    message: str


# ---------------------------------------------------------------------------
# Root record
# ---------------------------------------------------------------------------


class StructuredOverlap(BaseModel):
    """The interchange record between the spatial stage and the text engine.

    Producers: the live spatial stage, or an imported workbook.
    Consumer: the text engine.

    This is the contract. Both stages depend on this module and on nothing of each
    other. See docs/PROJECT_PLAN.md section 2.7.
    """

    schema_version: str = Field(
        SCHEMA_VERSION,
        description="Contract schema version this record was written against",
    )
    tenure_id: str = Field(..., description="Identifier for the tenure (e.g. the INTRID_SID)")
    source_type: SourceType

    generated_at: datetime | None = Field(
        None, description="When the spatial stage produced this record (fabric is time-varying)"
    )
    generator_version: str | None = Field(
        None, description="lds package version that produced the record"
    )

    tenure_area_ha: float = Field(..., ge=0)
    area_method: str = Field(
        ...,
        description="How tenure_area_ha was derived, e.g. "
        "'TENURE_AREA_IN_HECTARES (Tantalis attribute)' or 'SDO_GEOM.SDO_AREA, EPSG:3005'",
    )
    oracle_sdo_tolerance: float | None = Field(
        None, description="The SDO tolerance used for the spatial ops, for traceability"
    )

    parcels: list[OverlapParcel] = Field(
        default_factory=list,
        description="In-scope parcels that will appear in the description (Tantalis, "
        "plus any provisional PMBC-fallback parcels for PID-gap portions).",
    )
    unsurveyed_remainders: list[UnsurveyedRemainder] = Field(default_factory=list)

    out_of_scope_flags: list[OutOfScopeFlag] = Field(default_factory=list)
    data_maintenance_flags: list[DataMaintenanceFlag] = Field(default_factory=list)
    validation_messages: list[ValidationMessage] = Field(default_factory=list)

    # --- convenience predicates (no business logic, just record inspection) ---

    @property
    def is_refused(self) -> bool:
        """True if any out-of-scope flag would block a complete description.

        Note: a PID-gap (data_maintenance_flags) does NOT make the tenure refused —
        it still gets a complete draft with flagged provisional text. Only
        out_of_scope_flags represent genuine refusal conditions.
        """
        return len(self.out_of_scope_flags) > 0

    @property
    def has_provisional_text(self) -> bool:
        """True if any parcel uses PMBC/PID fallback text (PID-gap present)."""
        return any(p.provisional for p in self.parcels)

    @property
    def land_districts(self) -> list[str]:
        """Distinct land districts across parcels AND unsurveyed remainders, in
        first-seen order (parcels first).

        Remainders count: the single/multi-district wording rules depend on every
        district the description will mention, and an unsurveyed-only tenure has
        districts only on its remainders.
        """
        seen: list[str] = []
        for p in self.parcels:
            if p.land_district not in seen:
                seen.append(p.land_district)
        for r in self.unsurveyed_remainders:
            if r.land_district is not None and r.land_district not in seen:
                seen.append(r.land_district)
        return seen

    @property
    def is_multi_district(self) -> bool:
        return len(self.land_districts) > 1
