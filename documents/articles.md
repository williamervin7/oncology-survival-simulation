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