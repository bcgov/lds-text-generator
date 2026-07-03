"""Architecture boundary tests — real assertions, pass now.

Enforces the dependency directions that keep the design sound:

    contracts  <-  spatial      (spatial depends on contracts only)
    contracts  <-  engine       (engine depends on contracts only; PURE)
    contracts  <-  llm          (the model adapter implements the engine's
                                 parser Protocol structurally; no engine import)
    everything <-  webapp       (the UI may import anything; nothing imports it)

If a rule here fails, the boundary has been violated: the engine is no longer
independently testable, or the model is no longer strictly optional.
"""

from __future__ import annotations

import ast
from pathlib import Path

SRC = Path(__file__).parent.parent / "src" / "lds"

HEAVY_DEPS = (
    "oracledb",
    "geopandas",
    "shapely",
    "pyproj",
    "fiona",
    "pandas",
    "openpyxl",
)
WEB_DEPS = ("dash", "flask")
MODEL_DEPS = ("ollama",)

# package dir -> import prefixes it must never use
FORBIDDEN: dict[str, tuple[str, ...]] = {
    "engine": ("lds.spatial", "lds.llm", "lds.webapp") + HEAVY_DEPS + WEB_DEPS + MODEL_DEPS,
    "contracts": ("lds.spatial", "lds.engine", "lds.llm", "lds.webapp")
    + HEAVY_DEPS
    + WEB_DEPS
    + MODEL_DEPS,
    "spatial": ("lds.engine", "lds.llm", "lds.webapp") + WEB_DEPS + MODEL_DEPS,
    "llm": ("lds.spatial", "lds.engine", "lds.webapp") + HEAVY_DEPS + WEB_DEPS,
}


def _imported_modules(py_file: Path) -> set[str]:
    tree = ast.parse(py_file.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names.add(node.module)
    return names


def test_dependency_directions_hold():
    violations: list[str] = []
    for package, forbidden_prefixes in FORBIDDEN.items():
        for py_file in (SRC / package).rglob("*.py"):
            for module in _imported_modules(py_file):
                for prefix in forbidden_prefixes:
                    if module == prefix or module.startswith(prefix + "."):
                        violations.append(f"{package}/{py_file.name} imports {module}")
    assert not violations, "boundary violations:\n" + "\n".join(violations)
