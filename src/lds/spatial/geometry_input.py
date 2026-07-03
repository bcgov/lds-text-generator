"""Geometry input: resolve a tenure to one canonical polygon in BC Albers.

Two entry paths, both producing the same canonical geometry:
  - by Tantalis INTRID_SID: look the geometry up in BCGW (no binding needed).
  - by submitted file: read shp / gdb / kml / geojson / etc.

For submitted geometry the order is deliberate:
    read -> validate/repair IN NATIVE CRS -> reproject to EPSG:3005 -> dissolve
(repairing an invalid self-intersecting polygon before reprojection avoids the
transformation distorting or failing on bad geometry).

Uploaded-file rules (enforced here / surfaced to the UI):
  - shapefiles arrive as a ZIP (a shapefile is several sibling files);
  - a File Geodatabase may hold multiple layers -> select / auto-detect one polygon
    layer;
  - missing CRS is a BLOCKING error (never assume a projection);
  - mixed geometry types are rejected unless polygonal features can be extracted;
  - multiple features are dissolved to one polygon, with a warning;
  - geometry repair is reported, never hidden.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CanonicalGeometry:
    """A validated tenure polygon ready for overlay.

    geometry is held as WKB bytes so it can be bound to Oracle as a BLOB without
    re-importing shapely at the boundary. crs is always EPSG:3005 here.
    """

    wkb: bytes
    crs_epsg: int = 3005
    repaired: bool = False
    dissolved_feature_count: int = 1
    warnings: list[str] = field(default_factory=list)


def load_from_intrid_sid(intrid_sid: str) -> CanonicalGeometry:
    """Look up the tenure geometry in BCGW by Tantalis parcel id.

    No geometry binding is needed for this path (the geometry already lives in
    Oracle); this returns the canonical form for any client-side needs.
    """
    raise NotImplementedError("Phase 2: query TA_CROWN_TENURES_SVW by INTRID_SID")


def load_from_file(path: Path, layer: str | None = None) -> CanonicalGeometry:
    """Read a submitted geometry file and return the canonical polygon.

    Args:
        path: the uploaded file (a .zip for shapefiles; a .gdb path; .kml; .geojson).
        layer: for multi-layer sources (GDB), the chosen layer; None to auto-detect
            a single polygon layer (and error if ambiguous).

    Raises:
        ValueError: missing CRS, no polygonal features, ambiguous layer, etc.
            (blocking validation errors — fail loudly, never guess).
    """
    raise NotImplementedError(
        "Phase 3: read formats, validate/repair in native CRS, reproject, dissolve. "
        "Check KML driver availability FIRST (gdb + wkb are proven; kml is not)."
    )
