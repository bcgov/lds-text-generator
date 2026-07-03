"""Spatial integration tests against live BCGW (Phases 2-3).

Marked `bcgw`: conftest skips them automatically unless BCGW_USER /
BCGW_PASSWORD / BCGW_DSN are set, so the suite runs offline. These are the
known-answer and binding-confirmation tests — implement the bodies in their
phases; the marker mechanism already works.
"""

import pytest

bcgw = pytest.mark.bcgw


@bcgw
def test_id_path_overlay_on_known_tenures_is_schema_valid():
    # Phase 2: run build_overlap_from_intrid_sid on a few known tenures; assert
    # schema-valid, non-empty where expected, and generated_at/area_method set.
    # (Human checkpoint validates correctness separately.)
    raise NotImplementedError("Phase 2: implement against live BCGW")


@bcgw
def test_large_geometry_wkb_blob_binding_roundtrip():
    # Phase 3: bind a large, many-vertex geometry as WKB/BLOB, reconstruct via
    # SDO_UTIL.FROM_WKBGEOMETRY, overlay, assert schema-valid output.
    raise NotImplementedError("Phase 3: implement against live BCGW")
