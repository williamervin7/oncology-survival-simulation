# Missingness Audit
 
Documents the per-column review of SEER "special code" values (sentinel codes
used for unknown/not-applicable/not-documented, which differ by field) prior
to modeling. Global blanket recoding (a single missing-value list applied
across all columns) was identified as a defect in `convert_missing_values()`
(see CHANGELOG 0.3.0) and replaced with explicit, field-specific handling.
 
**Method:** ran `value_counts(dropna=False)` on each of the 36 columns in the
cleaned analytic cohort (Stage III colon cancer, SEER Research Data,
2010–2023), flagged any column containing common SEER sentinel-code patterns
(`9`, `99`, `999`, `9999`, `88`, text sentinels), then verified the actual
meaning of each flagged code against the SEER Program's field documentation
(Dictionary of SEER Variables / Data Description for SEER Research and
Research Plus) rather than assuming a generic convention applies.
 
## Disposition Table
 
| Column | Flagged value(s) | Count | Meaning (per SEER field documentation) | Disposition |
|---|---|---|---|---|
| Survival months | `9`, `88`, `99` | 120 / 73 / 64 | Genuine duration values (9, 88, and 99 months of survival) — this field's range legitimately spans these numbers. Not a categorical sentinel field. | Kept as-is. Not missing. |
| Time (derived from Survival months) | `9`, `88`, `99` | 120 / 73 / 64 | Same as above — `Time` is a direct derivation of `Survival months`. | Kept as-is. Not missing. |
| Regional nodes examined (1988+) | `9` | 158 | Exact count: field allows `01–89` as literal node counts. `9` = 9 nodes examined. | Kept as-is. Not missing. |
| Regional nodes examined (1988+) | `88` | 2 | Exact count: `88` falls within the valid `01–89` count range (88 nodes examined) — distinct from the AJCC staging field's use of `88` as "not applicable." | Kept as-is. Not missing. |
| Regional nodes examined (1988+) | `99` | 4 | Unknown whether nodes were removed. | Recoded → NaN via `resolve_special_codes()`. |
| Regional nodes positive (1988+) | `9` | 259 | Exact count: 9 positive nodes. Same `01–89` convention as nodes examined. | Kept as-is. Not missing. |
| Regional nodes positive (1988+) | `99` | 8 | Unknown whether nodes were positive. | Recoded → NaN via `resolve_special_codes()`. |
| RX Summ--Surg Prim Site (1998-2022) | `99` | 2 | Site-specific surgery code field (codes vary by cancer site per SEER Appendix C). `99` inferred as unknown/not stated by SEER's general trailing-9s convention; not directly confirmed against the colon-specific code table for this field. | Recoded → NaN via `resolve_special_codes()`. Low impact (n=2). Flagged as an inference, not a confirmed field-specific citation — follow-up: verify against Appendix C if this field is used further. |
| Age recode with single ages and 90+ | — | 0 flagged | Field checked for missingness after `str.extract()` parsing; confirmed complete (age is a near-universally captured field in cancer registry data). | No missing values found. See `seer_field_selection_rationale.md` for the field-selection history (single-ages vs. ranged-bin recode). |
| Stage (consolidated) | `III`, `IIINOS` | 153 / 51 (204 total) | Confirmed Stage III with unspecified AJCC substage — cannot be assigned to IIIA/IIIB/IIIC. Not a missing-value sentinel in the traditional sense, but functionally unusable for substage-adjusted analysis. | Excluded from the substage-adjusted analytic cohort (n=14,239 remaining from n=14,443). See CHANGELOG 0.7.0 — this exclusion also resolved a silent reference-category contamination bug in `pd.get_dummies(..., drop_first=True)`, where `III` (alphabetically first) was being dropped as the implicit reference instead of `IIIA`. |
| Sex | — | 0 flagged | Complete; binary Female/Male values only. | No missing values found. |
| Chemotherapy recode (yes, no/unk) | — | 0 flagged as missing | Field itself combines two distinct states ("No" and "Unknown") into a single `No/Unknown` category — a SEER-defined collapsing, not something introduced by this pipeline. | Kept as SEER-defined. Documented as a modeling limitation: cannot distinguish confirmed non-receipt from unknown receipt status. See also immortal-time-bias note below. |
 
## Columns Not Yet Audited
 
The full audit covers the columns entering the current candidate covariate
set (age, sex, substage, node counts, surgery, chemotherapy) plus the
duration/event fields. Remaining columns in the 36-column cleaned extract
(e.g., tumor grade, histology) have not yet been run through this process —
planned when those covariates are evaluated for the second-pass model (see
CHANGELOG "Planned" sections).
 
## Known Limitations Surfaced During This Audit (Not Missingness, But Related)
 
- **Chemotherapy receipt / immortal time bias:** patients must survive long
  enough after diagnosis/surgery to receive adjuvant chemotherapy, so
  "received chemo" partially encodes "survived long enough to get it" rather
  than a clean baseline treatment assignment. The univariate HR for this
  covariate (~0.32) should be read as an upper-bound estimate of protective
  effect, not a causal estimate. This is a feature-exclusion-window /
  information-leakage concern under Phase 1's requirements and is being
  addressed separately (see CHANGELOG "Planned" — chemo-receipt handling
  decision).
## Process Note (for future column checks)
 
1. Run the `value_counts(dropna=False)` loop on the target column(s).
2. Flag any hits against `FLAGGED_PATTERNS` (text sentinels, generic numeric
   unknowns, not-applicable numeric codes) as *candidates for review*, not
   confirmed missingness.
3. Verify the actual code meaning for that specific field via the SEER
   Dictionary of Variables / Data Description PDF — do not assume a code's
   meaning transfers across fields (e.g., `88` means "not applicable" in the
   AJCC stage field but is a legitimate node count in the nodes-examined
   field).
4. Log the disposition here regardless of outcome (including "checked, no
   special codes found") so this file remains the single source of truth for
   what has and has not been reviewed.