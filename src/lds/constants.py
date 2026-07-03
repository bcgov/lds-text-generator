"""Calibrated constants shared across the tool.

These values are deliberate, calibrated choices (see docs/PROJECT_PLAN.md). They
are collected here so there is a single source of truth and so the calibration
values can be tuned in one place once measured against real tenures.

IMPORTANT: the threshold/tolerance numbers marked "CALIBRATE" are placeholders to
be pinned from real data before spatial production. Do not treat the placeholder
numbers as final.
"""

from __future__ import annotations

# --- whole vs part -----------------------------------------------------------
# A parcel is "whole" if the tenure covers at least this fraction of it, else
# "part". Author-WHOLE parcels sit at the coverage ceiling (per-parcel
# diagnostic, tests/fixtures/discovery/: n=21, median 1.000, p10 0.9996), so the
# cutoff sits just under 1.0 to absorb edge-rounding noise.
#
# PROVISIONAL — known caveats from the discovery calibration
# (tests/fixtures/discovery/threshold_calibration_calib2*.csv):
#   - the sweep grid was 0.005 steps, so 0.999 itself was never tested (the
#     tool now includes a fine grid, 0.990..1.000 step 0.0005 — re-run it);
#   - best on-grid agreement was at 1.0 with only ~72%, because 400 of 964
#     author-PARTIAL parcels sit at/above 0.999 coverage — a contamination
#     (parser attribution noise / fabric drift / authoring convention) that a
#     threshold cannot fix. Investigate a sample of those cases at the Phase 2
#     checkpoint before trusting whole/part flags in bulk (see
#     docs/open_questions.md).
WHOLE_PART_THRESHOLD: float = 0.999        # provisional; see caveats above

# --- sliver / minimum meaningful overlap -------------------------------------
# A parcel is included in the overlay only if the intersection is meaningful, to
# reject boundary-mismatch slivers. Include if EITHER threshold is met (i.e.
# exclude only when the intersection is tiny both absolutely and relatively).
# CALIBRATE both from real tenures (same exercise as WHOLE_PART_THRESHOLD).
MIN_INTERSECTION_AREA_M2: float = 1.0      # CALIBRATE
MIN_INTERSECTION_RATIO: float = 0.001      # CALIBRATE

# --- Right-of-Way refusal gate ------------------------------------------------
# A SEPARATE, higher gate decides whether a Right-of-Way overlap is meaningful
# enough to flag the tenure ROW-related (out of v1 scope). Deliberately not the
# sliver gate above: the costs are asymmetric. A false parcel inclusion costs one
# extra row a reviewer deletes; a false ROW flag costs the whole automation for
# that tenure — and tenures commonly share boundary slivers with road ROWs.
# CALIBRATE from real tenures; expect these to sit well above the sliver gate.
ROW_MEANINGFUL_MIN_AREA_M2: float = 100.0  # CALIBRATE
ROW_MEANINGFUL_MIN_RATIO: float = 0.01     # CALIBRATE

# --- unsurveyed remainder floor ------------------------------------------------
# A remainder below this area is treated as overlay noise, not an unsurveyed
# component (the discovery tool used the same 0.01 ha). CALIBRATE.
REMAINDER_MIN_HA: float = 0.01             # CALIBRATE

# --- Oracle SDO ---------------------------------------------------------------
# One tolerance constant, used consistently for intersection, difference, union,
# area, and distance. CALIBRATE / confirm against the layer metadata before use.
ORACLE_SDO_TOLERANCE: float = 0.005        # CALIBRATE / confirm

# --- coordinate reference system ---------------------------------------------
# All overlay work happens in BC Albers. Submitted geometry is validated/repaired
# in its native CRS first, then reprojected to this.
WORKING_EPSG: int = 3005                   # NAD83 / BC Albers

# --- output formatting --------------------------------------------------------
# Area is rounded to this many decimals in the final description (deliberate
# rounding, calibrated; the source data carries spurious extra precision).
AREA_DECIMALS: int = 2

# Small-area guard: blanket 2-decimal rounding misstates tiny tenures (a real
# 0.0225 ha description would become "0.02" — an 11% error — or even "0.00").
# If rounding to AREA_DECIMALS changes the area by more than this relative
# error, keep extending the decimals until it does not. See docs/rules.md
# ("Area"); confirm the convention against the registry.
AREA_MAX_RELATIVE_ROUNDING_ERROR: float = 0.005   # CALIBRATE / confirm

# --- named-feature candidate generation --------------------------------------
# Predictable bounds for vicinity/foreshore candidate lookup. The human confirms
# the actual feature; these only bound what is proposed. CALIBRATE search radius.
# The remaining search parameters (distance source geometry, foreshore priority,
# unnamed/duplicate handling) are specified in docs/PROJECT_PLAN.md section 9b.
FEATURE_SEARCH_RADIUS_M: float = 5000.0    # CALIBRATE
FEATURE_MAX_CANDIDATES_PER_TYPE: int = 5

# --- optional model fallback --------------------------------------------------
# The optional Ollama parser is disabled by default and guarded by a timeout so it
# degrades to "flag for manual entry" rather than hanging on constrained hardware.
LLM_FALLBACK_ENABLED_BY_DEFAULT: bool = False
LLM_TIMEOUT_SECONDS: float = 30.0
