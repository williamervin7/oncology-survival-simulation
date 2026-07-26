# Oncology Survival Analysis & Patient-Level Markov Microsimulation

An applied data science and clinical biostatistics framework built to model time-to-event oncology data, map continuous survival curves to discrete state transition probabilities, and execute a patient-level Monte Carlo microsimulation for disease progression support.

## Project Intent & Scope
Rather than framing analytics purely around predictive accuracy metrics (e.g., AUC/ROC), this project focuses on clinical decision support by modeling lifetime health state trajectories. The architecture is deliberately separated into two key disciplines:
1. **Biostatistical Survival Modeling:** Estimating parametric and semi-parametric time-to-event outcomes while explicitly testing mathematical invariants and checking proportional hazards assumptions.
2. **Health Economics/Outcomes Decision Simulation:** Utilizing the survival model outputs to parameterize a discrete-time Markov state-transition model evaluated via patient-level microsimulation.

## Repository Architecture

```text
├── data/
│   ├── raw/                 # Immutable source datasets
│   └── processed/           # Filtered cohorts with documented leakage prevention
├── documents/
│   ├── articles.md/         # Summary of all articles read
├── src/
│   ├── __init__.py
│   ├── models.py            # Kaplan-Meier, Cox PH, and parametric survival engines
│   ├── simulation.py        # Patient-level Monte Carlo microsimulation loop
│   └── validation.py        # Statistical calibration and internal validation utilities
├── tests/
│   ├── software/            # Standard unit tests for code correctness (shapes, types)
│   └── statistical/         # Mathematical invariant checks (e.g., conservation of probability)
├── notebooks/               # Exploratory data analysis and interactive visualization
├── environment.yml          # Pinned, reproducible environment specification
├── CHANGELOG.md             # Version tracking anchored on explicit iteration logic
└── README.md

```

## Methodology & Reporting Standards

To ensure reproducibility and analytical alignment with clinical research benchmarks, this project adapts guidelines from the following methodologies:

* **STROBE / TRIPOD Statements:** Utilized to govern cohort selection, handle data censoring mechanisms transparently, and structure regression transparency.
* **ISPOR-SMDM Modeling Good Research Practices:** Applied to document state-to-state transition probability derivations, cycle-length adjustments, and structural validation of the simulation model.

## Implementation Roadmap

### Phase 1: Semi-Parametric & Non-Parametric Survival Analysis

* Process survival data accounting for right-censoring mechanisms.
* Implement non-parametric baseline estimators (Kaplan-Meier).
* Fit Cox Proportional Hazards models; execute explicit statistical testing of the Proportional Hazards assumption (Schoenfeld residuals).
* Enforce explicit feature exclusion windows to prevent time-dependent covariate information leakage.

### Phase 2: Machine Learning Extensions & Calibration

* Implement a Random Survival Forest (RSF) model to evaluate non-linear interactions.
* Score and contrast models utilizing the Concordance Index (C-index) and Brier Score trajectories over time.
* Evaluate discrimination vs. calibration metrics to assess out-of-sample stability.

### Phase 3: Mathematical Derivation & Markov Transition Modeling

* Convert survival functions into multi-state discrete-time transition probabilities.
* Structure health states (e.g., Stable Disease, Progression, Death).
* Implement half-cycle corrections to prevent discrete step timing distortions.

### Phase 4: Patient-Level Monte Carlo Microsimulation

* Construct a vectorized simulation engine to scale individual patient trajectories.
* Execute Monte Carlo iterations utilizing a centralized, reproducible random number generator (RNG) framework.
* Perform structural validation (internal consistency checks matching aggregate simulated curves back to empirical Kaplan-Meier curves).
