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