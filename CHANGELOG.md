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