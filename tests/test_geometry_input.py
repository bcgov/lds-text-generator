"""Phase 3 — submitted-geometry reading and validation rules (mostly DB-independent).

Uses small synthetic geometries. Failing placeholders define the upload rules.
"""

import pytest


@pytest.mark.skip(reason="Phase 3: missing CRS must be a blocking error")
def test_missing_crs_raises():
    raise NotImplementedError


@pytest.mark.skip(reason="Phase 3: multiple features dissolve with a warning")
def test_multifeature_dissolves_and_warns():
    raise NotImplementedError


@pytest.mark.skip(reason="Phase 3: invalid polygon repaired and repair reported")
def test_invalid_geometry_repaired_and_reported():
    raise NotImplementedError


@pytest.mark.skip(reason="Phase 3: non-polygon input rejected")
def test_non_polygon_rejected():
    raise NotImplementedError
