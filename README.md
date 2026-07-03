# LDS Generator

[![Lifecycle:Experimental](https://img.shields.io/badge/Lifecycle-Experimental-339999)](https://github.com/bcgov/repomountie/blob/master/doc/lifecycle-badges.md)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

Generates **Legal Description Schedule** text for BC Land Act Crown land tenures, in
support of Land Authorizations.

Given a tenure — as a Tantalis Parcel ID or an uploaded geometry — the tool runs the
GIS overlay against the BC survey-parcel fabric (BCGW), determines which parcels are
covered (wholly or partly), the area, and any unsurveyed remainder, then generates
the formal legal description and validates it. A person stays in control: the tool
produces a draft and flags anything uncertain for review.

## Architecture

Two stages connected by a contract:

```
tenure (ID or geometry) -> [ spatial stage ] -> StructuredOverlap -> [ text engine ] -> legal description
```

- **Spatial stage** (`src/lds/spatial/`): Oracle + GeoPandas. Overlay runs
  server-side in BCGW; GeoPandas handles geometry I/O.
- **Contract** (`src/lds/contracts/`): the `StructuredOverlap` interchange record —
  an inspectable intermediate. Both stages depend on it; neither imports the other.
- **Text engine** (`src/lds/engine/`): pure Python, no DB/web. Deterministic rules
  produce the legal text; an optional model fallback (disabled by default) only
  helps parse the hardest input strings.

## Getting started

```bash
uv sync
uv run pytest -q
uv run lds --help
```

Windows desktop: run `setup.bat`.

BCGW access (for the spatial stage) is configured via environment variables
(`BCGW_USER`, `BCGW_PASSWORD`, `BCGW_DSN`); never commit credentials.


## Status

Scaffold. The contract and the architecture are in place; modules are stubbed with
contracts and tests. Build proceeds in phases: contract → spatial stage (ID path,
with a human validation gate) → submitted geometry → text engine → pipeline/CLI →
review UI → optional model.

## License

Copyright 2026 Province of British Columbia

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
these files except in compliance with the License. You may obtain a copy of the
License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
