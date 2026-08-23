## [0.1.0] - 2026-07-18
### Added
- Initial repository scaffold: directory structure, pinned environment.yml, README with methodology framework (STROBE/TRIPOD/ISPOR-SMDM alignment).
- No modeling code yet — this commit establishes architecture ahead of Phase 1 implementation.

## [0.2.0] - 2026-08-16
### Added
- Introductory `lifelines` exploration using built-in practice datasets (Walton, lung, Rossi): fit Kaplan-Meier survival curves and a Cox proportional hazards model on Rossi to establish baseline familiarity with the library API before applying it to project data.
- First pass at real project data: loaded SEER-derived rectal cancer cohort (`Survival months`, `Event`), fit Kaplan-Meier survival curve, exported plot.
- Cox PH model on rectal cohort with `Year of diagnosis` and `Sex` as covariates (n=197,170; 64,942 events observed). Both covariates significant (p<0.005); effect sizes modest (HR 0.99 and 1.11 respectively). Concordance 0.52 — expected given only two weak covariates included so far.

### Fixed
- Corrected a `CoxPHFitter.fit()` call where duration/event columns were passed positionally instead of by keyword, causing `Year of diagnosis` to be silently treated as the event column and the real `Event` column to be pulled in as a covariate. Re-fit with explicit `duration_col`/`event_col` keyword arguments resolved the issue; number of events observed now correctly matches the source data (64,942) rather than equaling total row count.

### Notes
- Full SEER column set identified for incremental covariate testing (site, year of diagnosis, sex, age, cause-specific death classification). Adding covariates one at a time to isolate encoding issues as they arise — `Age recode` and `Site recode` are both text-binned/categorical fields expected to need explicit handling before inclusion.
- This SEER pull is a practice dataset for debugging workflow, not the final dataset for the project.

## [0.3.0] - 2026-08-22

### Added
- `cleaning.py`: `get_data()` function to load raw SEER case listing CSV from `data/raw/`.
- `cleaning.py`: `convert_missing_values()` function to standardize SEER missing-value codes to NaN and derive `Time`/`Event` columns.
- `eda.ipynb`: Introduction markdown cell documenting notebook purpose, population, and primary endpoint. Called both get_data() and convert_missing_values() to ensure they ran properly

### Fixed
- `Event` flag in `convert_missing_values()` was initially derived from `SEER cause-specific death classification`, which encodes cause-specific survival. Corrected to use `Vital status recode (study cutoff used)` to align with the project's overall survival (OS) endpoint decision.

### Known issues / follow-ups
- `convert_missing_values()` applies a single global list of missing-value patterns (`Blank(s)`, `Unknown`, `999`, `9999`, `99`) across all columns. SEER missing codes are field-specific and this risks nulling legitimate values in some columns (e.g., `Regional nodes examined`/`positive` use their own missing codes with different meanings). Needs per-column handling.
- Staging fields span two non-overlapping eras: `Derived AJCC Stage Group, 7th ed (2010-2015)` and `Derived EOD 2018 Stage Group Recode (2018+)`. Diagnosis years 2016-2017 are not covered by either field and will need explicit handling when merging into a unified `Stage` column.
- `BASE_DIR` path resolution in `cleaning.py` uses `os.path.dirname(os.getcwd())`, which is fragile to working directory changes. Consider switching to a `pathlib`-based path anchored to the script/module location.

### Environment / tooling
- Resolved Windows conda setup: broken `menuinst`-generated Start Menu shortcut, missing PATH registration, and PowerShell execution policy (`Restricted`) blocking the `conda init` profile hook.
- Resolved a hung VS Code Jupyter kernel (stuck on "Restarting") via disabling/re-enabling the Jupyter extension; confirmed via a working JupyterLab session outside VS Code that the environment itself was healthy.

## [0.4.0] - 2026-08-23

### Added
- `cleaning.py`: `derive_stage_2018()` — primary Stage derivation for diagnosis years 2018+, mapping `Derived EOD 2018 Stage Group Recode (2018+)` directly to a harmonized `Stage` column (0, I, IIA-C, IIIA-C, IVA-C, plus bare II/III/IV for cases where sub-stage is confirmed unknown).
- `cleaning.py`: `derive_stage_2018_tnm_validation()` — independent Stage derivation built from `Derived EOD 2018 T/N/M Recode` fields and AJCC 8th edition stage-grouping tables (colon/rectum), retained as a documented QA cross-check against the primary derivation rather than the production path.
- `articles.md`: four new source entries — AJCC Stage II (Table 3), Stage III (Table 4), and Stage IV (Table 5) definitions (PDQ/NCI, reprinted from AJCC Cancer Staging Manual 8th ed.), plus AJCC 6th edition general TX/NX/MX definitions (with edition-mismatch limitation noted).
- `seer_field_selection_rationale.md`: added staging field selection table (2010-2015 / 2016-2017 / 2018+ source fields) and resolved the open question on whether `Derived EOD 2018 Stage Group Recode` is a true AJCC 8th edition stage group (confirmed via SEER EOD 2018 training documentation).

### Fixed
- `stage_map` in `derive_stage_2018()` was initially missing a mapping for code `"0"` (Stage 0 has no A/B/C sub-split, so the bare code is already complete) — corrected, recovering 470 rows that had been incorrectly falling through to unstaged/NaN.
- Bare sub-stage-unknown codes (`"2"`, `"3"`, `"4"` — confirmed major stage, unknown A/B/C sub-stage) were being excluded entirely; reclassified as valid `"II"`/`"III"`/`"IV"` values so confirmed Stage III cases aren't dropped from the cohort solely for missing sub-stage detail. Recovered 64 legitimate Stage III rows.
- `np.select()` in `derive_stage_2018_tnm_validation()` raised a `TypeError` on this NumPy version when mixing string choices with an `np.nan` default; fixed by using a string sentinel (`"UNSTAGED"`) and converting to `NaN` via `pandas.Series.replace()` afterward.

### Investigated
- SEER code `88` (T/N/M/Stage Group fields) confirmed as "AJCC staging schema not applicable" via SEER EOD 2018 General Coding Instructions; verified against data (all 125 rows with T=88 also show Stage Group=88, 100% consistent, all malignant behavior). Histologic Type ICD-O-3 follow-up identified these as predominantly neuroendocrine-family tumors (goblet cell carcinoid, composite carcinoid/MANEC) — staged under separate AJCC chapters, not colon adenocarcinoma TNM. Excluded from analytic cohort.
- SEER code `99` (Stage Group Recode) confirmed as genuine "Unknown" (insufficient documentation, historical, or death-certificate-only cases), consistent with SEER's 9/99 convention across other staging fields. 1,417 rows excluded as legitimately unstageable.
- Cross-validated `derive_stage_2018()` (pre-derived field) against `derive_stage_2018_tnm_validation()` (independently built from T/N/M + AJCC tables): 18,283/21,061 rows agree (86.4%) after correcting for a `NaN`-comparison artifact; remaining disagreement concentrated in known ambiguous sub-code cases (bare T4, bare N2 with T2/T3, bare M1), consistent with the pre-derived field having access to more granular underlying data than the public T/N/M recode fields alone.
- Identified the 2016-2017 staging gap bridge field: `7th Edition Stage Group Recode (2016-2017)`, added to SEER*Stat session and re-exported.

### Known issues / follow-ups
- Stage derivation for 2010-2015 (`Derived AJCC Stage Group, 7th ed`) and 2016-2017 (`7th Edition Stage Group Recode`) not yet implemented — same direct-mapping pattern as `derive_stage_2018()`, planned next.
- Three era-specific Stage columns still need to be merged into one harmonized `Stage` column.
- Possible appendix-site (C18.1) contamination in the "colon" cohort, flagged by a single `Tis(LAMN)` row during the code-88 histology investigation — not yet formally checked.
- `convert_missing_values()` blanket missing-value list still applies globally rather than per-column (carried over from 0.3.0, not addressed today).
- `BASE_DIR` path resolution still uses `os.path.dirname(os.getcwd())` (carried over from 0.3.0, not addressed today).

### Environment / tooling
- `np.select()` dtype-mismatch behavior differs from older NumPy versions when combining string choices with a float `np.nan` default — worth a project-wide note if other derivation functions use this pattern later.