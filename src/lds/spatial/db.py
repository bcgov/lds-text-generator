"""Oracle (BCGW) connectivity for the spatial stage.

Uses oracledb in THIN mode (no Instant Client) so the desktop install stays clean.
Provides the connection and the WKB-as-BLOB bind helper used to hand
Python-originated geometry to Oracle for server-side overlay.

Confirmed working in prior projects; covered here by an integration test with a
large, many-vertex geometry (see tests/test_spatial_db.py). Do not switch to WKT
(VARCHAR2 size limit) or RAW (32767 limit) — bind WKB as a BLOB and reconstruct
server-side with SDO_UTIL.FROM_WKBGEOMETRY.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager


class BcgwConfig:
    """Connection settings for BCGW. Credentials come from the environment /
    secrets, never hard-coded. (Concrete fields filled in during Phase 2.)"""

    def __init__(
        self,
        user: str,
        password: str,
        dsn: str,
    ) -> None:
        self.user = user
        self.password = password
        self.dsn = dsn

    @classmethod
    def from_env(cls) -> BcgwConfig:
        """Build config from environment variables (BCGW_USER, BCGW_PASSWORD,
        BCGW_DSN). Raises a clear error if any are missing."""
        raise NotImplementedError("Phase 2: read BCGW_USER / BCGW_PASSWORD / BCGW_DSN from env")


@contextmanager
def connect(config: BcgwConfig | None = None) -> Iterator[object]:
    """Yield an oracledb thin-mode connection to BCGW.

    Args:
        config: connection settings; if None, build from environment.

    Yields:
        An open oracledb Connection, closed on exit.
    """
    raise NotImplementedError("Phase 2: open an oracledb thin-mode connection and yield it")


def bind_geometry_as_wkb_blob(cursor: object, wkb: bytes, bind_name: str = "geom_wkb") -> None:
    """Bind a geometry's WKB bytes as a BLOB parameter on the given cursor.

    The query reconstructs the geometry server-side via
    SDO_UTIL.FROM_WKBGEOMETRY(:geom_wkb). This is the thin-mode-safe handoff for
    Python-originated geometry (the submitted-geometry path).

    Args:
        cursor: an oracledb cursor.
        wkb: geometry as WKB bytes (shapely geom.wkb).
        bind_name: the bind variable name used in the SQL.
    """
    raise NotImplementedError("Phase 3: bind `wkb` as a BLOB parameter under thin mode")
