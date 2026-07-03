"""Overlay: the core of the spatial stage.

Runs the tenure-vs-fabric overlay SERVER-SIDE in Oracle (the fabric is already
indexed there), computes the per-parcel measurements, classifies the remainder,
runs PMBC detection, and assembles a StructuredOverlap.

The heavy spatial work (intersection, SDO_GEOM areas, coverage ratio,
SDO_DIFFERENCE remainder) runs in Oracle and returns text + numbers, not bulk
geometry — with ONE exception: the remainder geometry itself is extracted once as
WKB (SDO_UTIL.TO_WKBGEOMETRY) because three downstream steps need it (the
per-district split, the PMBC signal-1 cross-overlay, and the named-feature
candidate lookup). All dataset/column names come from lds.spatial.views — verify
the VERIFY-marked ones before first use.

The discovery tool tools/reconstruct_overlaps.py already implements the ID-path
overlay and is the REFERENCE IMPLEMENTATION to port here. Specifically:

  - parcel_overlap_sql()       -> the per-parcel intersection + coverage ratio query
                                  (SDO_ANYINTERACT join, SDO_GEOM.SDO_AREA of the
                                  parcel and of SDO_INTERSECTION, ratio, sliver
                                  filter). This is the core of build_overlap.
  - remainder_sql()            -> the unsurveyed-remainder area (SDO_AGGR_UNION of
                                  interacting parcels, SDO_DIFFERENCE from the
                                  tenure).
  - remainder_district_sql()   -> a STARTING POINT only (see porting note 5).
  - process_tenure()           -> the per-tenure orchestration (run the queries,
                                  derive WITHIN_Y_N from the ratio vs threshold).

Differences to apply when porting (the tool was a discovery instrument; this is
the production stage):
  1. DROP the `titled_only` toggle entirely — inclusion is Primary+Subdivision,
     title is not an input (see docs/rules.md).
  2. ROW: query ALL parcel types and assess ROW against the DEDICATED ROW gate
     (ROW_MEANINGFUL_MIN_* in constants — NOT the sliver gate; the costs are
     asymmetric). If meaningful ROW overlap exists, add the out-of-scope flag but
     KEEP BUILDING the rest of the overlap: the reviewer needs to see what else
     the tenure covers, and v2 (ROW categories) will want the data. The
     description itself stays refused via is_refused.
  3. CLAMP coverage_ratio into [0, 1] before assembly (tolerance noise can push
     the SQL ratio slightly above 1; the contract rejects > 1). Guard the NULL
     ratio case (NULLIF on a zero-area parcel): skip the row and record a
     validation message rather than crash.
  4. EXTRACT the remainder geometry as WKB (SDO_UTIL.TO_WKBGEOMETRY on the
     SDO_DIFFERENCE result) when its area >= REMAINDER_MIN_HA.
  5. SPLIT the remainder by land district: intersect it with the districts view
     and emit ONE UnsurveyedRemainder PER DISTRICT with per-district areas. The
     tool's remainder_district_sql() picks only the single largest district
     (FETCH FIRST 1) — that is NOT sufficient: the multi-district unsurveyed
     wording rule (docs/rules.md) needs every district.
  6. ADD PMBC detection. Signal 1 (main): overlay the remainder WKB against the
     PMBC fabric (views.PMBC_VIEW); a titled parcel under the remainder is a
     PID-gap -> emit a provisional PMBC-fallback parcel (parcel_type=None,
     land_district via spatial join to the districts view) + DataMaintenanceFlag.
     Signal 2 (secondary, flag-for-attention only): a null
     LAND_TITLE_OFFICE_IDENTIFIER on a matched SUBDIVISION-type parcel. Scope it
     to Subdivision parcels — untitled parcels are the NORM for Crown land, so an
     unscoped null-PID check would flag nearly every tenure (see docs/rules.md).
  7. EMIT a StructuredOverlap (contract), not the tool's xlsx sheet. Set
     generated_at, generator_version, area_method, oracle_sdo_tolerance. The
     tool's sheet columns (OVERLAP_LEGAL_DESCRIPTION, WITHIN_Y_N, AREA_HA,
     UNSURVEYED_LAND_DISTRICT, PHYSICAL_FEATURE) map onto contract fields.
  8. An unknown INTRID_SID raises ValueError with a clear message (the CLI
     reports it); it does not produce an empty overlap.

Order of operations (docs/PROJECT_PLAN.md sections 8a, 8b, 5.3a/b):
  1. Query ALL intersecting parcel types (including Right-of-Way).
  2. Assess ROW overlap against the ROW gate; if meaningful, add the ROW
     out-of-scope flag (description refused) and continue building for review.
  3. Build the overlay from allowed types (Primary + Subdivision; title not used).
  4. Apply the sliver rule: include a parcel only if the intersection is
     meaningful (MIN_INTERSECTION_AREA_M2 OR MIN_INTERSECTION_RATIO).
  5. Compute coverage_ratio (clamped) and the whole/part flag per parcel.
  6. Compute the remainder (tenure minus union of matched parcels); if
     >= REMAINDER_MIN_HA, extract its WKB and split it per land district.
  7. For the remainder, run the no-overlap decision tree:
       - PMBC cross-overlay (signal 1) -> titled parcel missing from Tantalis =
         PID-gap: emit provisional PMBC-fallback parcel + DataMaintenanceFlag.
       - foreshore evidence -> unsurveyed foreshore remainder (in scope).
         (The foreshore/upland classifier layers are an open item — see
         docs/open_questions.md before implementing this branch.)
       - upland vicinity feature/district -> unsurveyed upland remainder (in scope).
       - grid-only -> out of scope (v1).
       - none -> insufficient evidence -> out of scope (manual review).
  8. Null-PID heuristic (signal 2) on matched SUBDIVISION parcels: flag likely
     data-currency issues for attention (secondary; docs/PROJECT_PLAN.md 5.3b).
"""

from __future__ import annotations

from lds.contracts.overlap import StructuredOverlap
from lds.spatial.db import BcgwConfig
from lds.spatial.geometry_input import CanonicalGeometry


def build_overlap_from_intrid_sid(
    intrid_sid: str,
    config: BcgwConfig | None = None,
) -> StructuredOverlap:
    """Produce a StructuredOverlap for an existing tenure, by Tantalis id.

    This is the Phase 2 deliverable and the primary validation path: its output
    can be checked against the tenure's real legal description (known-answer test)
    and inspected by a person before the text engine is built.

    Raises:
        ValueError: the INTRID_SID does not exist in the tenures view.
    """
    raise NotImplementedError("Phase 2: ID-path overlay -> StructuredOverlap")


def build_overlap_from_geometry(
    geometry: CanonicalGeometry,
    tenure_id: str,
    config: BcgwConfig | None = None,
) -> StructuredOverlap:
    """Produce a StructuredOverlap for a submitted geometry.

    Binds the geometry to Oracle as WKB/BLOB (db.bind_geometry_as_wkb_blob),
    reconstructs server-side, and runs the same overlay as the ID path. Phase 3.
    """
    raise NotImplementedError("Phase 3: submitted-geometry overlay -> StructuredOverlap")
