"""Dash application factory. Phase 6.

Dash is Flask under the hood, so this same app runs locally (setup.bat) now and on
OpenShift later as a deployment change, not a rewrite.
"""

from __future__ import annotations


def create_app() -> object:
    """Build and return the Dash app (a Flask app). Phase 6."""
    raise NotImplementedError("Phase 6: build the Dash review UI")


if __name__ == "__main__":
    # `python -m lds.webapp.app` is the documented launch command; make it do
    # something visible even before Phase 6 lands.
    app = create_app()
    app.run(debug=False)  # type: ignore[attr-defined]
