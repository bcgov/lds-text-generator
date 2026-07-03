# Discovery-phase data (committed reference copies)

Copied 2026-07-03 from two discovery working folders on the team's internal
share (full paths recorded locally in `docs/data_locations.md`, which is not
published): the calibration workspace (BCGW extracts pulled 2026-06-18,
calibration outputs) and the AI_demo folder (the May 2026 baseline experiment;
see below).

Tantalis tenure records are public-registry data.

| File | What it is | Used for |
| --- | --- | --- |
| `Query_2_result.csv` | 200 tenures: INTRID_SID, CROWN_LANDS_FILE, DISPOSITION_TRANSACTION_SID, validated LEGAL_DESC, AREA_HA, PURPOSE/SUBPURPOSE, LOCATION_TEXT, REGION, EXPIRY | The known-answer set. Phase 2 golden-fixture capture (tools/capture_fixtures.py) and Phase 5 end-to-end checks. |
| `Query_4_result.csv` | 84 descriptions labelled by FAMILY (ROW, grid, ...) | Phase 4 classifier refusal tests: real ROW phrasing families and grid-only (NTS/PNG) references. |
| `RANKED_202606181331.csv` | 362 descriptions stratified by complexity (STRATUM, COMMA_COUNT, DESC_LEN) | Parser test corpus for Phase 4 (docs/parsing_complexity.md is derived from material like this). |
| `threshold_calibration_calib2.csv` | The whole/part threshold sweep (0.90–1.00, step 0.005) | Provenance for WHOLE_PART_THRESHOLD — see the caveats in constants.py and docs/open_questions.md. |
| `threshold_calibration_calib2_perparcel.csv` | Per-parcel diagnostic behind the sweep (985 aligned parcels) | The basis for the calibration caveats: author-WHOLE n=21 (median coverage 1.000); 400 of 964 author-PARTIAL parcels sit at/above 0.999 coverage. |
| `multi_shape.xlsx` | The 9-sheet overlay workbook from the baseline experiment (columns: OVERLAP_LEGAL_DESCRIPTION, WITHIN_Y_N, AREA_HA) | THE reference for the workbook input format (`lds.workbook`, Phase 6); also the sheets behind the baseline run. |
| `complex_shape.xlsx` | Single-sheet workbook with the full column set (adds PHYSICAL_FEATURE, UNSURVEYED_LAND_DISTRICT) | Workbook-format reference for the unsurveyed-land columns. |
| `batch_results.docx` | The baseline experiment's OUTPUT: descriptions a general AI model produced from multi_shape.xlsx + the instruction prompt (May 2026) | **The baseline comparison fixture** (PROJECT_PLAN 5.2/10). NOT golden fixtures — these are unvalidated model outputs, kept to document the before/after (e.g. Sheet 3 contains the known whole/part error). Never use as expected output. |

The instruction document that drove the baseline (and that defines the
authoritative category 1-12 templates) is kept locally at
`docs/instructions/commonplace_AI_legal_description_instructions.txt`
(docs/ is untracked by design).

## Query 2 — generating SQL (run 2026-06-18)

```sql
SELECT
    t.INTRID_SID,
    t.CROWN_LANDS_FILE,
    t.DISPOSITION_TRANSACTION_SID,
    t.TENURE_LEGAL_DESCRIPTION   AS legal_desc,
    t.TENURE_AREA_IN_HECTARES    AS area_ha,
    t.TENURE_PURPOSE             AS purpose,
    t.TENURE_SUBPURPOSE          AS subpurpose,
    t.TENURE_LOCATION            AS location_text,
    t.RESPONSIBLE_BUSINESS_UNIT  AS region,
    t.TENURE_EXPIRY              AS expiry
FROM WHSE_TANTALIS.TA_CROWN_TENURES_VW t
WHERE t.TENURE_LEGAL_DESCRIPTION IS NOT NULL
  AND t.TENURE_STAGE  = 'TENURE'
  AND t.TENURE_STATUS = 'DISPOSITION IN GOOD STANDING'
  AND t.TENURE_EXPIRY > SYSDATE                       -- still active
  AND t.TENURE_EXPIRY > ADD_MONTHS(SYSDATE, -240)     -- proxy: commenced within ~20 yrs
ORDER BY t.DISPOSITION_TRANSACTION_SID DESC           -- newest disposition activity first
FETCH FIRST 200 ROWS ONLY
```

Notes: the sample is the 200 NEWEST active dispositions with a description —
deliberately recency-biased (fabric drift is lowest for recent tenures) but not
category-stratified; the capture subset for golden fixtures still needs manual
curation across categories. The query reads `TA_CROWN_TENURES_VW` (attribute
view); the overlay itself uses the spatial view `TA_CROWN_TENURES_SVW`.

Notes recorded from inspecting `Query_2_result.csv`:

- All 200 INTRID_SIDs are unique. 181 distinct dispositions — 5 dispositions hold
  more than one interest parcel. In four of those the parcels carry distinct
  LEGAL_DESCs (descriptions are per interest parcel); disposition 954468 has two
  parcels sharing one LEGAL_DESC. Keep this in mind at the Phase 2 granularity
  check (docs/open_questions.md).
- The generating SQL for the numbered queries is not in the repo; it lives with
  the discovery notes. Record it here when available.

Still off-repo (in the discovery folder): `calibration_candidates.csv`,
`Query_3a_result.csv` (source of the committed land-district snapshot),
`Query_3b_result.csv`, `reconstructed_overlaps*.xlsx`, the reconstruction
reports, `PROJECT_PLAN.docx`, and the tool proposal.
