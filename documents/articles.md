## Survival Analysis Part I: Basic Concepts and First Analyses

- **Source / Title:** Clark TG, Bradburn MJ, Love SB, Altman DG. (2003). *British Journal of Cancer*, 89(2), 232–238.
- **Cancer Site / Population:** Ovarian cancer cohort (n=825, Western General Hospital, Edinburgh) & non-small cell lung cancer phase III trial (n=164, radiotherapy vs. radiotherapy+CAP).
- **Event Definition:** Death or disease recurrence/relapse (time-to-event $T$).
- **Censoring:** Right-censoring (patients surviving past study duration or lost to follow-up).
- **Tools / Functions Used:** Kaplan-Meier survival curve, log-rank test, hazard functions $h(t)$, cumulative hazard $H(t)$.

### Summary
- **Core Concepts:** Explains why standard statistical methods (like linear regression or standard t-tests) fail on survival data due to skewness and right-censoring.
- **Kaplan-Meier Estimation:** Outlines non-parametric step-function estimation for $S(t)$ and how risk sets decrease as events occur or patients are censored.
- **Comparing Groups:** Introduces the log-rank test to evaluate whether observed vs. expected event counts differ significantly across treatment groups.

### Relevance to My Project / Code Pipeline
- Phase: 1 | Feeds into: KM curve reporting standard.
- Provides the foundational theoretical context needed before implementing Kaplan-Meier fitters or log-rank tests in code (`lifelines` / `scikit-survival`).


## Survival Analysis Part II: Multivariate Data Analysis — An Introduction to Concepts and Methods

- **Source / Citation:** Bradburn MJ, Clark TG, Love SB, Altman DG (2003). *British Journal of Cancer*, 89, 431–436. doi:10.1038/sj.bjc.6601119
- **Cancer Site / Population:** Two example datasets — (1) Ovarian cancer patients (prognostic index dataset from Clark et al, 2001); (2) Non-small cell lung cancer (NSCLC) trial patients
- **Event Definition (T):** Ovarian dataset — Overall Survival (death from any cause); Lung dataset — Relapse-free survival (time from diagnosis to cancer recurrence)
- **Censoring Mechanism (C):** Right-censored; for the lung dataset, patients were also censored at time of death if no recurrence had occurred (competing-risk-like censoring rule)
- **Tools / Statistical Methods Used:** Cox (semi-parametric) PH model; parametric PH models (Weibull, Exponential, Gompertz); Accelerated Failure Time (AFT) models (Log-Normal, Log-Logistic, Generalised Gamma, Weibull); Aalen's additive hazard model; stratified logrank analysis; brief mention of classification trees and neural networks as alternatives

### Key Findings & Summary
- Introduces the **Cox PH model**: h(t) = h₀(t)·exp{b₁x₁ + ... + bₚxₚ}, where the baseline hazard h₀(t) is estimated non-parametrically, making it distribution-free and the most widely used multivariate survival method.
- Demonstrates the Cox model on the ovarian cancer dataset (FIGO stage, histology, grade, ascites, age): higher FIGO stage, higher grade, presence of ascites, and increased age all significantly worsened survival (e.g., FIGO stage multivariate HR = 2.08, 95% CI 1.82–2.37).
- Contrasts **parametric PH models** (which assume a specific hazard distribution, e.g., Weibull) with the Cox model — parametric models are more informative (allow direct prediction of survival/hazard/median survival times) and slightly more statistically efficient, but require correct distributional specification.
- Introduces **AFT models**, where covariates act multiplicatively on the survival *time* rather than the hazard: log(T) = b₀ + b₁x₁ + ... + bₚxₚ + ε, with exp(bᵢ) interpreted as *time ratios* rather than hazard ratios. Illustrated using the lung cancer trial: adjuvant chemo + radiotherapy vs radiotherapy alone gave a time ratio of ~2.05 (95% CI 1.29–3.23), i.e., roughly doubled time to recurrence (predicted median survival ~16 months vs ~8 months).
- Notes that AFT and PH models coincide when survival times follow a Weibull distribution.
- Briefly covers **stratified survival analysis** (simple but doesn't scale to many covariates) and **Aalen's additive hazard model** (allows time-varying, non-constant covariate effects on the hazard scale, but is hard to interpret and rarely used in practice due to limited software support).
- Flags model-choice guidance as the subject of the next paper in the series: check proportional hazards assumption, distributional fit, and covariate selection.

### Relevance to My Project / Code Pipeline
- Foundational reference for choosing between **Cox PH** (`lifelines.CoxPHFitter`, R `survival::coxph`) vs **parametric AFT models** (`lifelines.WeibullAFTFitter`, `LogNormalAFTFitter`, etc.) depending on whether hazard-ratio or time-ratio interpretability is preferred.
- Useful baseline/comparison point: hazard ratios vs time ratios give different but related interpretations of the same covariate effects — good for reporting or sanity-checking model output in my pipeline.
- The proportional hazards assumption discussion is directly relevant to any Cox model diagnostics I implement (e.g., Schoenfeld residuals, log-log survival plots).
- Aalen's additive model could be worth exploring if I suspect time-varying covariate effects (non-proportional hazards) in my dataset, though tooling support is limited.
- Table structure (univariate vs multivariate HR/TR with 95% CI) is a good template for presenting my own model outputs.

### AJCC Colon Cancer Staging — Stage II Definitions (Table 3)
- **Source / Citation:** PDQ Adult Treatment Editorial Board. *Colon Cancer Treatment (PDQ®): Health Professional Version*. National Cancer Institute (US), 2002– . Table 3, "Definitions of TNM Stages IIA, IIB, and IIC" (reprinted with permission from AJCC: Colon and rectum. In: Amin MB, Edge SB, Greene FL, et al., eds. *AJCC Cancer Staging Manual*, 8th ed. New York, NY: Springer, 2017, pp 251–74). https://www.ncbi.nlm.nih.gov/books/NBK65858/table/CDR0000062687__584/
- **Cancer Site / Population:** Colon and rectum, AJCC 8th edition TNM
- **Event Definition ($T$):** N/A — staging reference table, not a survival study
- **Censoring Mechanism ($C$):** N/A
- **Tools / Statistical Methods Used:** N/A

#### Key Findings & Summary
- Stage IIA = T3, N0, M0; Stage IIB = T4a, N0, M0; Stage IIC = T4b, N0, M0.
- Confirms Stage II is defined entirely by tumor depth (T) with no nodal involvement (N0); the T4a/T4b split is the sole distinguishing factor between IIB and IIC.

#### Relevance to My Project / Code Pipeline
- Used to validate the harmonized `Stage` column derivation and to confirm the boundary logic separating Stage II from Stage III (specifically, the T4a/T4b distinction that also matters for IIIC per Table 4).


### AJCC Colon Cancer Staging — Stage III Definitions (Table 4)
- **Source / Citation:** PDQ Adult Treatment Editorial Board. *Colon Cancer Treatment (PDQ®): Health Professional Version*. National Cancer Institute (US), 2002– . Table 4, "Definitions of TNM Stages IIIA, IIIB, and IIIC" (reprinted with permission from AJCC: Colon and rectum. In: Amin MB, Edge SB, Greene FL, et al., eds. *AJCC Cancer Staging Manual*, 8th ed. New York, NY: Springer, 2017, pp 251–74). https://www.ncbi.nlm.nih.gov/books/NBK65858/table/CDR0000062687__580/
- **Cancer Site / Population:** Colon and rectum, AJCC 8th edition TNM
- **Event Definition ($T$):** N/A — staging reference table
- **Censoring Mechanism ($C$):** N/A
- **Tools / Statistical Methods Used:** N/A

#### Key Findings & Summary
- Stage IIIA: T1–T2, N1/N1c, M0 or T1, N2a, M0. Stage IIIB: T3–T4a, N1/N1c, M0 or T2–T3, N2a, M0 or T1–T2, N2b, M0. Stage IIIC: T4a, N2a, M0 or T3–T4a, N2b, M0 or T4b, N1–N2, M0.
- N sub-splits carry explicit node-count thresholds: N1a = 1 node, N1b = 2–3 nodes, N1c = 0 nodes but tumor deposits present; N2a = 4–6 nodes, N2b = 7+ nodes.
- Confirmed via independent cross-reference (AJCC Hindgut Taskforce validation, PMC2815715) that the T/N/M-to-stage-group mapping is identical between 7th and 8th edition for colon cancer — meaning this single table is valid for both the 2010–2015 and 2018+ portions of the cohort.

#### Relevance to My Project / Code Pipeline
- This is the primary source table for Stage III cohort flagging logic. Used directly to spot-check the pre-derived `Derived AJCC Stage Group, 7th ed` and `Derived EOD 2018 Stage Group Recode` fields against their underlying T/N/M values (e.g., confirmed row 1 [T1, IIIA] and row 3 [T4b, IIIC] against this table).


### AJCC Colon Cancer Staging — Stage IV Definitions (Table 5)
- **Source / Citation:** PDQ Adult Treatment Editorial Board. *Colon Cancer Treatment (PDQ®): Health Professional Version*. National Cancer Institute (US), 2002– . Table 5, "Definitions of TNM Stages IVA, IVB, and IVC" (reprinted with permission from AJCC: Colon and rectum. In: Amin MB, Edge SB, Greene FL, et al., eds. *AJCC Cancer Staging Manual*, 8th ed. New York, NY: Springer, 2017, pp 251–74). https://www.ncbi.nlm.nih.gov/books/NBK65858/table/CDR0000062687__575/
- **Cancer Site / Population:** Colon and rectum, AJCC 8th edition TNM
- **Event Definition ($T$):** N/A — staging reference table
- **Censoring Mechanism ($C$):** N/A
- **Tools / Statistical Methods Used:** N/A

#### Key Findings & Summary
- Stage IV is Any T, Any N, subdivided entirely by M: IVA = M1a (metastasis to one site/organ, no peritoneal involvement), IVB = M1b (two or more sites/organs, no peritoneal involvement), IVC = M1c (peritoneal surface metastasis, alone or with other sites).

#### Relevance to My Project / Code Pipeline
- Not part of the Stage III cohort definition directly, but needed to confirm the full 0–IV boundary set so Stage III can be positively identified (not just inferred by elimination). Also clarifies that the 388 rows with a bare, non-subdivided `M1` value cannot be placed into IVA/B/C — same ambiguous-code handling issue flagged for bare T4/N1/N2 rows.


### AJCC 6th Edition — General TX/NX/MX Definitions
- **Source / Citation:** Massachusetts Department of Public Health (Massachusetts Cancer Registry). *Staging Data* [training reference document], based on AJCC Cancer Staging Manual, 6th ed. Springer-Verlag, New York, 2002. https://www.mass.gov/doc/staging-data-0/download
- **Cancer Site / Population:** General TNM framework (site-agnostic)
- **Event Definition ($T$):** N/A — coding reference document
- **Censoring Mechanism ($C$):** N/A
- **Tools / Statistical Methods Used:** N/A

#### Key Findings & Summary
- Defines the generic TX/T0/Tis, NX/N0, MX/M0/M1 categories used as shared boilerplate across all AJCC site chapters. TX/NX/MX = "cannot be assessed or is unknown" for the respective TNM component.
- **Important limitation:** this source is explicitly 6th edition (2002). The N sub-splits (N1a/b/c, N2a/b) used in this project's cohort (7th/8th ed.) did not exist in 6th edition — this source is only valid for the generic TX/NX/MX "cannot be assessed" definitions, not for any site-specific or stage-grouping logic.

#### Relevance to My Project / Code Pipeline
- Confirms TX is a universal AJCC convention (not colon-specific, not a different cancer type) — resolved the question of why TX doesn't appear in the Stage III grouping table (Table 4): by definition, an unassessable T category cannot be placed in any determinable stage group.