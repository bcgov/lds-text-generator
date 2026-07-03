"""BCGW dataset names used by the spatial stage — single source of truth.

Every view/column the overlay touches is named here, each with its verification
status. VERIFY items must be checked with a `DESC <view>` (or a one-row SELECT)
against BCGW before first use in Phase 2/3 — do not trust them silently, and
update the status comment once checked.

The Tantalis names were verified during discovery (tools/reconstruct_overlaps.py).
The PMBC and land-district names are the standard catalogue names but have NOT
been used by the discovery tool; the FWA/GNS names come from the project plan
(docs/PROJECT_PLAN.md section 2.3a).
"""

from __future__ import annotations

# --- Tantalis: tenure geometry (VERIFIED in discovery) -------------------------
TENURE_VIEW = "WHSE_TANTALIS.TA_CROWN_TENURES_SVW"
TENURE_ID_COL = "INTRID_SID"
TENURE_GEOM_COL = "SHAPE"
TENURE_AREA_COL = "TENURE_AREA_IN_HECTARES"

# --- Tantalis: survey-parcel fabric (VERIFIED in discovery) --------------------
PARCEL_VIEW = "WHSE_TANTALIS.TA_SURVEY_PARCELS_SVW"
PARCEL_GEOM_COL = "SHAPE"
PARCEL_LEGAL_COL = "PARCEL_LEGAL_DESCRIPTION"
PARCEL_ID_COL = "PIN_SID"
PARCEL_TYPE_COL = "PARCEL_TYPE"              # Primary / Subdivision / Right-of-Way
PARCEL_PID_COL = "LAND_TITLE_OFFICE_IDENTIFIER"  # non-null => titled (PID)

# --- Tantalis: land districts (used in discovery; re-VERIFY columns) -----------
LAND_DISTRICT_VIEW = "WHSE_TANTALIS.TA_LAND_DISTRICTS_SVW"
LAND_DISTRICT_NAME_COL = "LAND_DISTRICT_NAME"    # VERIFY
LAND_DISTRICT_GEOM_COL = "SHAPE"

# --- PMBC: titled-parcel fabric for PID-gap detection (VERIFY ALL) --------------
# Signal 1 overlays the unsurveyed remainder against this fabric; a titled parcel
# under the remainder is a PID-gap. Column names are the expected catalogue
# names — VERIFY every one before Phase 2 sign-off.
PMBC_VIEW = "WHSE_CADASTRE.PMBC_PARCEL_FABRIC_POLY_SVW"  # VERIFY
PMBC_GEOM_COL = "SHAPE"                                   # VERIFY
PMBC_PID_COL = "PID"                                      # VERIFY
PMBC_LEGAL_COL = "PARCEL_LEGAL_DESCRIPTION"               # VERIFY (fallback text source)
PMBC_OWNER_TYPE_COL = "OWNER_TYPE"                        # VERIFY (may help filter)

# --- Named features for vicinity / foreshore clauses (from plan 2.3a; VERIFY) --
FWA_BAYS_AND_CHANNELS_VIEW = "WHSE_BASEMAPPING.FWA_BAYS_AND_CHANNELS_POLY"
FWA_STREAM_NETWORKS_VIEW = "WHSE_BASEMAPPING.FWA_STREAM_NETWORKS_SP"
FWA_LAKES_VIEW = "WHSE_BASEMAPPING.FWA_LAKES_POLY"
FWA_NAME_COL = "GNIS_NAME"                                # VERIFY per view (may be GNIS_NAME_1)
GNS_VIEW = "WHSE_BASEMAPPING.GNS_GEOGRAPHICAL_NAMES_SP"
GNS_NAME_COL = "GEOGRAPHICAL_NAME"                        # VERIFY
GNS_FEATURE_TYPE_COL = "FEATURE_TYPE"                     # VERIFY
