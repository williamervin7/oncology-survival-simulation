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

## [0.5.0] - 2026-08-28

### Added
- `.github/workflows/ci.yml`: GitHub Actions CI pipeline using `conda-incubator/setup-miniconda` against `environment.yml` (single source of truth, no `requirements.txt` duplication). Runs flake8 lint (syntax/undefined-name errors as hard failures, complexity/line-length as warnings) and pytest, split into `tests/software/` and `tests/statistical/` steps.
- `pyproject.toml`: `[tool.pytest.ini_options] pythonpath = ["."]` so `src`-based imports resolve under plain `pytest` invocation, not just `python -m pytest`.
- `tests/statistical/test_placeholder.py`: skip-marked placeholder so CI has a defined, visible reason for zero collected tests until Cox/RSF/Markov statistical tests exist, rather than relying on treating pytest exit code 5 as a pass.
- `tests/software/test_cleaning.py`: placeholder fuction `test_shape()` with the exit code pass

### Fixed
- `ModuleNotFoundError: No module named 'src'` in CI-only pytest runs — local runs worked because `python -m pytest` adds the repo root to `sys.path` automatically; direct `pytest` invocation (as used in CI) does not. Resolved via `pythonpath` config above rather than changing local run habits.

### Known issues / follow-ups
- `tests/software/test_cleaning.py` currently exercises `get_data()` against the real SEER extract in `data/raw/`, which is `.gitignore`d (correctly, per SEER data use terms) and therefore absent on the CI runner. CI has not yet been run against this test file post-import-fix; expect a failure here next. Needs a small synthetic fixture CSV (`tests/fixtures/`) matching real column names/codes but fabricated values, covering known edge cases (AJCC code `88`, 2016–2017 staging-gap years) — not yet built.
- `BASE_DIR` fragile-path issue (flagged in 0.3.0) is now more urgent: CI runs from a different working-directory context than local Windows runs and is a more reliable way to surface this bug than manual local testing.

### Environment / tooling
- Confirmed CI runner resolves to Python 3.11.16 / pytest 9.1.1 inside the `oncology-survival-sim` conda env (matches `environment.yml` `name:` field; explicit `activate-environment` set in workflow for self-documentation).

### Planned (next session)
- Implement `derive_stage_2010_2015()` and `derive_stage_2016_2017()` (same direct-mapping pattern as `derive_stage_2018()`).
- Merge all three era-specific Stage columns into one harmonized `Stage` column.
- Run coverage/count checks by diagnosis year and stage; verify Stage III counts specifically across all three eras.
- Investigate possible C18.1 (appendix) contamination in the cohort before declaring it finalized

## [0.6.0] - 2026-08-29

### Added
- `cleaning.py`: `derive_stage_2018()`, `derive_stage_2018_tnm_validation()`, `consolidate_stage()`, and `get_stage_III()` — full AJCC staging harmonization pipeline resolving the 2016-2017 field gap by combining 7th edition (2010-2015), 7th edition recode (2016-2017), and EOD 2018 (2018+) sources into a single `Stage` column.
- `cleaning.py`: `save_cleaned_data()` and `clean_process()` — end-to-end orchestration function running the full pipeline (load → convert missing → event flag → stage derivation → consolidation → Stage III filter) with step-by-step audit printouts.
- `src/config.py`: new centralized config module — `RANDOM_SEED`, `DEFAULT_TIME_HORIZON`, `STAGE_THREE_CODES`, `STAGE_THREE_SIZE` (verified against cleaned data, N=14,443), and `PROJECT_ROOT`/`DATA_DIR` anchored via `Path(__file__)`.
- `tests/software/test_cleaning.py`: test coverage added for `convert_missing_values()`, `event_flag()`, `derive_stage_2018()`, `consolidate_stage()`, and `get_stage_III()`.
- `.github/workflows/ci.yml`: GitHub Actions pipeline running `pytest tests/software/` on push.
- `eda.ipynb`: Part 1 (data exploration) started — cohort definition markdown, data load, row-count integrity check against `STAGE_THREE_SIZE`, `Time`/`Event` distribution histograms and summary statistics, overall Kaplan-Meier curve for the Stage III cohort with trajectory/clinical-insights writeup.

### Fixed
- `BASE_DIR` path resolution in `cleaning.py` (`get_data()`, `save_cleaned_data()`) switched from `os.path.dirname(os.getcwd())` to `Path(__file__).resolve().parents[2]`, removing the working-directory dependency flagged in 0.3.0. Surfaced as a real, reproducible failure once CI began running from a different working-directory context than local runs — confirming this wasn't just a theoretical risk.
- `eda.ipynb` data-load cell updated to import `DATA_DIR` from `src/config.py` instead of re-deriving `BASE_DIR` via `os.path.dirname(os.getcwd())` — same fragile-path pattern just fixed in `cleaning.py`, now propagated to the notebook so path resolution has a single source of truth.
- `event_flag()`: `Event` was derived via `np.where(vital_status == "Dead", 1, 0)`, which can never produce `NaN` — meaning `dropna(subset=["Event"])` was dead code, and any row with unrecognized/missing vital status was silently coded as censored (`Event = 0`) rather than dropped or flagged. Corrected to map unrecognized vital status explicitly to `NaN` so those rows are excluded rather than miscoded as survivors.
- AJCC stage code `0` (in `Derived EOD 2018 Stage Group Recode (2018+)`) confirmed as genuine AJCC Stage 0 (in situ), not a missing-data placeholder — resolves the open question from 0.3.0. Does not affect the Stage III cohort either way, since `"0"` was never in the Stage III filter, but closes out the staging-code verification work. (Code `88` was already confirmed as "not applicable" prior to this session.)

### Known issues / follow-ups
- `convert_missing_values()`'s per-column missing-code handling (flagged in 0.3.0) is still outstanding — needed before covariate-level EDA proceeds past `Time`/`Event`.
- `derive_stage_2018_tnm_validation()` exists as a cross-check derivation against PDQ/NCI T/N/M stage-grouping tables but is not yet wired into `clean_process()` or reconciled against `derive_stage_2018()`'s output.

### Notes
- Decided to split `eda.ipynb` into two notebooks going forward: `eda.ipynb` for data exploration (distributions, missingness, univariate/bivariate covariate checks) and a new `modeling.ipynb` for Cox PH / RSF fitting and comparison — keeping exploratory and model-development work separated for cleaner TRIPOD-aligned reporting.
- Next planned step: covariate-level EDA (distributions, per-field missingness, stratified KM by candidate covariate, collinearity check) before moving into `modeling.ipynb`.

## [0.7.0] - 2026-09-04

### Added
- `models.py`: `resolve_special_codes()` — recodes SEER field-specific `99` sentinel values to NaN in `Regional nodes examined (1988+)`, `Regional nodes positive (1988+)`, and `RX Summ--Surg Prim Site (1998-2022)`. Deliberately does not touch codes like `9`/`88` in the node-count fields, which are legitimate exact counts (SEER allows 01-89 as real values), not missing-value codes.
- `cleaning.py`: age-parsing logic for `Age recode with single ages and 90+` — strips ` years` suffix, top-codes `90+` to `90`, casts to float.
- `models.py`: `univariate_model()` and `run_univariate_screen()` — fit single-covariate Cox PH models for reporting/comparison purposes only (not used as a selection filter for the multivariable model, per TRIPOD guidance).
- `models.py`: `preprocessing()` — binary-encodes `Sex` and `Chemotherapy recode (yes, no/unk)`, one-hot encodes `Stage` substage with `drop_first=True` (IIIA as reference category), with input-validation assertions to fail loudly on unexpected category values.
- `modles.py`: `remove_stage_III()`  - removes cases coded `III` or `IIINOS`
- Cohort restriction: excluded 204 cases coded `III` or `IIINOS` (unspecified substage) from substage-adjusted analyses, since they cannot be assigned to IIIA/IIIB/IIIC and were silently becoming part of the dummy-encoded reference group.
- `tests/software/test_cleaning.py`: coverage for age-parsing function, including genuinely missing (`NaN`) input and unparseable text, both expected to return NaN without raising.
- `tests/software/test_cleaning.py`: coverage for `preprocessing()`, including full three-category Stage encoding, reference-category exclusion, dtype checks written to be platform-independent (Windows `int32` vs. Linux CI `int64`), and rejection of malformed input via the new validation assertions.
- `seer_field_selection_rationale.md`: replaced `Age recode with <1 year olds and 90+` entry with `Age recode with single ages and 90+`, documenting the side-by-side comparison used to confirm the two fields derive from the same underlying age value before dropping the ranged-bin version.

### Fixed
- `resolve_special_codes()`: corrected `df[cols].replace(...)` (which silently dropped all non-target columns) to `df_clean[cols] = df_clean[cols].replace(...)`, preserving the full dataframe.
- Data pipeline bug: original SEER pull included `Age recode with <1 year olds and 90+` (5-year ranged bins, e.g. "60-64 years") rather than a continuous covariate. Re-extracted with `Age recode with single ages and 90+` for single-year resolution.

### Findings
- Univariate Cox PH screen on Stage substage (IIIA reference, n=14,239) surfaced a non-monotonic hazard pattern: IIIC HR = 2.13 (expected direction), but IIIB HR = 0.73 — lower hazard than the nominally milder IIIA. Confirmed via literature search that this is a documented phenomenon in colon cancer staging research ("staging paradox"), attributed to nodal status outweighing tumor depth as a survival predictor, rather than a pipeline defect. Ruled out reference-category contamination (from the `III`/`IIINOS` exclusion) as the cause — estimates were materially unchanged after exclusion.

### Known issues / follow-ups
- `RX Summ--Surg Prim Site (1998-2022)` code `99` recoded to NaN on inferred SEER convention (trailing-9s = unknown); exact field-specific definition not yet confirmed against SEER Appendix C documentation.
- Chemotherapy receipt covariate likely subject to immortal time bias (patients must survive long enough to receive adjuvant chemo) — current univariate HR (0.32) should be treated as an upper-bound estimate of protective effect, not a causal estimate. Flag for discussion/limitations section.

### Planned (next session)
1. Decide and implement chemo-receipt handling for information leakage: choose between excluding chemo from the Phase 1 model, a landmark analysis, or a formal time-varying covariate — document the rationale before implementing.
2. Build `model_eda.ipynb`: run Kaplan-Meier on the final analytic cohort (overall + stratified by AJCC substage) as a visual complement to the Cox output.
3. Fit the full multivariable Cox PH model in `model_eda.ipynb` using the finalized covariate set (post chemo-leakage decision).
4. Run `cph.check_assumptions()` against the fitted multivariable model; document per-covariate Schoenfeld residual results (not just pass/fail) and pre-commit remedy hierarchy (stratification before time-varying extension) before viewing results.
5. Continue domain-knowledge literature research on remaining candidate covariates (tumor grade/histology) to confirm second-pass inclusion list before RSF comparison phase begins.