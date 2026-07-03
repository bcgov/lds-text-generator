"""Named-feature candidate lookup for vicinity / foreshore clauses.

For an unsurveyed remainder, finds nearby named features and returns TYPED
candidates with distances for human confirmation. Never auto-selects.

Sources (docs/PROJECT_PLAN.md 2.3a; canonical names in lds.spatial.views):
  - foreshore water body : FWA_BAYS_AND_CHANNELS_POLY (GNIS_NAME)
  - watercourse          : FWA_STREAM_NETWORKS_SP     (GNIS_NAME)
  - named lake           : FWA_LAKES_POLY             (GNIS_NAME)
  - terrain / general     : GNS_GEOGRAPHICAL_NAMES_SP  (GEOGRAPHICAL_NAME, FEATURE_TYPE)

Search behaviour must follow docs/PROJECT_PLAN.md section 9b: configured radius
and per-type candidate cap (constants), a DOCUMENTED distance-source geometry
(pick nearest-point-on-remainder vs centroid and state it), intersecting
waterbody priority for foreshore, unnamed features skipped, duplicate names
across datasets de-duplicated with the source recorded.

For upland vicinity, filter the geographical-names layer to terrain types
(Mountain, Mount, Peak, Peaks, Summit, Ridge, Crag, Butte, Knob, Hill, Dome, ...).
Candidate generation is bounded by FEATURE_SEARCH_RADIUS_M and
FEATURE_MAX_CANDIDATES_PER_TYPE (constants). Features are often points (a mountain
is a labelled point); distances run across mixed geometry types, which is fine for
an approximate vicinity clause.
"""

from __future__ import annotations

from lds.contracts.overlap import CandidateFeature, RemainderType
from lds.spatial.db import BcgwConfig

# Terrain feature types used to filter the geographical-names layer for upland
# vicinity candidates. (Subset of the full FEATURE_TYPE vocabulary.)
TERRAIN_FEATURE_TYPES: tuple[str, ...] = (
    "Mountain",
    "Mount",
    "Peak",
    "Peaks",
    "Summit",
    "Ridge",
    "Crag",
    "Crags",
    "Butte",
    "Knob",
    "Knoll (2)",
    "Hill",
    "Hills",
    "Dome",
    "Domes",
    "Plateau",
    "Spur",
    "Pinnacle",
)


def find_candidate_features(
    remainder_wkb: bytes,
    remainder_type: RemainderType,
    config: BcgwConfig | None = None,
) -> list[CandidateFeature]:
    """Return typed nearest-feature candidates for a remainder.

    Args:
        remainder_wkb: the remainder geometry (WKB, EPSG:3005).
        remainder_type: FORESHORE -> query water bodies; UPLAND -> query lakes +
            terrain features; UNKNOWN -> query broadly and let the human decide.
        config: BCGW connection settings.

    Returns:
        Candidates with name, type, distance, and source dataset — NOT auto-selected.
    """
    raise NotImplementedError("Phase 2: query FWA + geographical-names; return typed candidates")
