# SEER Field Selection — Stage III Colon Cancer Extract

**Research question:** Does the choice of survival model (Cox PH vs. Random Survival Forest) used to parameterize a Markov microsimulation meaningfully change simulated long-term patient outcomes?

**Cohort scope:** Colon primary (C18.0–C18.9), malignant behavior, one primary only, diagnosis years 2010–2021.

This document justifies every field pulled in the SEER*Stat Case Listing extract, why it was included, and any known data quirks that affect downstream cleaning in Python. Organized to mirror the extract's column order.

---

## Cohort Definition Fields

| Field | Rationale |
|---|---|
| **Patient ID** | Unique row identifier for the extract. |
| **Site recode ICD-O-3/WHO 2008** | Used as the primary filter for "Colon excluding Rectum" — SEER's cleaner recode of raw site codes, reduces risk of miscoding rectosigmoid/rectal cases into the colon cohort. |
| **Primary Site – labeled** | Pulled as a Table column (not a filter) to independently verify the site filter worked correctly and to inspect subsite distribution (cecum vs. sigmoid vs. transverse, etc.) post-extraction. |
| **Year of diagnosis** | Defines the 2010–2021 window. Chosen to (1) sit inside a stable-enough AJCC staging period to permit harmonization across only two editions rather than several, (2) provide adequate follow-up time for survival analysis by excluding 2022–2023 diagnoses, which would be almost entirely short-follow-up/censored and add noise without signal, and (3) keep SEER registry coverage broad and consistent (post SEER-13/17 expansion). |
| **Sequence number** | Restricted to "One primary only" to avoid multiple-primary contamination — a patient with two independent primaries complicates both the survival endpoint definition and Markov state assignment. |
| **Type of Reporting Source** | Excludes autopsy-only and death-certificate-only cases, which have no real follow-up time and would corrupt survival estimation. Kept hospital, radiation/oncology center, lab, physician office, hospice, and outpatient/surgery center sources. |
| **Behavior recode for analysis** | Restricted to "Malignant" — excludes in situ/benign/borderline behavior, keeping the cohort clinically consistent with invasive colon cancer. |

---

## Staging Fields (critical — used to define Stage III)

**Why this section is complex:** SEER's AJCC-derived staging fields are edition-specific and do not span the full 2010–2021 window in a single field. The 2010–2021 range straddles two distinct staging systems:

| Diagnosis years | Staging system | Fields pulled |
|---|---|---|
| 2010–2017 | AJCC 7th edition | Derived AJCC Stage Group, T, N, M (7th ed) |
| 2018–2021 | EOD 2018 (SEER's designated successor scheme for this range — a true "Derived AJCC Stage Group, 8th ed" field was not available in this database version; confirmed via a direct field-name search) | Derived EOD 2018 Stage Group Recode, T, N, M Recode |

**Rationale for pulling both:** Rather than filtering on stage in SEER*Stat (which would silently drop any case with a blank/unknown value pre-export), both field families were pulled as Table columns only. This preserves every case that passed the cohort-definition filters, regardless of staging completeness, so stage harmonization and Stage III flagging happen transparently in Python where the logic is documented and version-controlled.

**Open question — not yet verified:** The extracted EOD 2018 Stage Group Recode field returns values (1, 2A/2B/2C, 3A/3B/3C, 4A/4B/4C, plus 0/88/99) that look like a near-direct numeric analog to AJCC stage groups (1↔I, 2↔II, 3↔III, 4↔IV). This is promising but unconfirmed. Before finalizing the Stage III harmonization logic, need to verify:
- Whether SEER's EOD 2018 documentation explicitly states this recode is intended as an AJCC-equivalent stage grouping, or is a related-but-distinct staging concept
- What the 0/88/99 codes represent (likely not-applicable/unknown, to be confirmed rather than assumed)
- Whether any known discontinuities exist between 7th ed AJCC and EOD 2018 at the T/N/M component level that would affect how cleanly IIIA/IIIB/IIIC maps onto 3A/3B/3C
If the mapping is confirmed clean, Stage III for 2018+ cases can likely be flagged directly from 3A/3B/3C. If not, a substitute approach (e.g., Regional Nodes Positive as a cross-check) will be needed and the resulting methodological deviation documented explicitly in the methods/limitations section. This verification is planned as part of the upcoming literature review week and will be updated here once resolved.

| Field | Rationale |
|---|---|
| **Regional Nodes Examined** | Edition-independent; part of Stage III definition (adequate lymphadenectomy) and used as a covariate. |
| **Regional Nodes Positive** | Edition-independent; primary driver of N-stage and a strong prognostic covariate in colon cancer for both Cox and RSF models. |
| **SEER historic stage A** | Coded consistently 1973–2015 without edition-splitting. Used as an independent cross-check on the harmonized AJCC Stage III flag — large disagreements between "Regional" (historic stage A) and the derived Stage III flag flag cases worth manual review. |

---

## Demographic / Patient-Level Covariates

| Field | Rationale |
|---|---|
| **Age recode with <1 year olds and 90+** | SEER does not release a fully continuous age field due to small-cell disclosure limits; this recode provides single-year resolution (00–89) with only ages 90+ top-coded into one category. Functionally equivalent to continuous age for modeling once parsed and flagged. Two SEER fields with "age" and "standard" in the name ("Age standard for survival" and "Age standard for survival, prostate") were considered and excluded — these are pre-built age bands for age-standardized survival comparisons, not raw age, and the prostate-specific version is irrelevant to this cohort. |
| **Sex** | Standard demographic covariate. |
| **Race recode (White, Black, Other)** | Standard demographic covariate; SEER's collapsed recode reduces small-cell sparsity relative to detailed race categories. |
| **Marital status at diagnosis** | Commonly used SES proxy in SEER survival literature; associated with both diagnosis stage at presentation and treatment completion. |

---

## Treatment Variables

| Field | Rationale |
|---|---|
| **Chemotherapy recode (yes, no/unk)** | Key treatment covariate. **Known limitation:** SEER's chemotherapy recode is not chemotherapy-registry-verified the way surgery is, and is known to undercount actual treatment receipt. Documented as a limitation, not silently accepted. |
| **Radiation recode** | Pulled for completeness/exclusion checks; less central to colon (vs. rectal) cancer treatment protocols but relevant for identifying any neoadjuvant/adjuvant radiation cases. |
| **RX Summ–Surg Prim Site (1998–2022)** | Primary surgical treatment covariate and candidate Markov state boundary (resected vs. unresected). The parallel "2023" field (4-character alphanumeric, introduced for diagnoses 2023+) was deliberately excluded once the diagnosis-year window was fixed at 2010–2021, since it would return entirely blank for this cohort. |

---

## Survival / Outcome Variables (dependent variable)

| Field | Rationale |
|---|---|
| **Survival months** | Time-to-event variable ($T$). **Known quirk:** SEER survival months has documented coding conventions distinguishing true "0 months" from missing/unknown — value labels checked before numeric casting to avoid silently corrupting the field. |
| **Vital status recode (study cutoff used)** | Primary event indicator (Alive/Dead). |
| **SEER cause-specific death classification** | Pulled despite Overall Survival (OS) being the primary endpoint — OS was deliberately chosen over cause-specific survival to avoid cause-of-death attribution ambiguity, which is a known source of misclassification bias in cancer registry data. This field is retained for a planned sensitivity analysis and to support discussion of the OS-vs-cause-specific tradeoff in limitations. |
| **COD to site recode** | More granular cause-of-death detail; used as a QC cross-check on the cause-specific classification above rather than a primary analytic variable. |
| **Year of follow-up recode** | Used to sanity-check that survival months is internally consistent with the follow-up window, since a direct date-of-last-contact field was not exposed in this SEER*Stat database version. |

---

## Fields Considered but Not Included

| Field | Reason excluded |
|---|---|
| **Registry ID / State-county recode** | Not available as a distinct field in this SEER*Stat database version. Would have supported a registry-level heterogeneity check; its absence is noted as a scope limitation, not a blocker for the core research question. |
| **Date of last contact (direct date field)** | Not exposed in this database version. Year of follow-up recode used as a substitute for survival-months QC. |
| **RX Summ–Surg Prim Site 2023 (2023+)** | Excluded once diagnosis years were capped at 2021 — this field only populates for 2023+ diagnoses and would be entirely blank. |
| **Median household income / Rural-Urban Continuum Code** | Considered as SES covariates but deprioritized for the initial extract; may be added in a later pull if SES adjustment becomes necessary. |

---

*Extract pulled via SEER*Stat, Case Listing Session, 61,281 records. Filters applied at selection: Colon excluding Rectum (C18.0–C18.9), malignant behavior, one primary only, diagnosis years 2010–2021, excluding autopsy/DCO reporting sources. No restrictions applied on staging, treatment, or outcome fields — all cases passing cohort filters are retained regardless of completeness in these columns.*
