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