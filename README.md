![Build Status](https://github.com/williamervin7/oncology-survival-simulation/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Conda](https://img.shields.io/badge/environment-conda-44A833?logo=anaconda)
![License](https://img.shields.io/github/license/williamervin7/oncology-survival-simulation)
![Last Commit](https://img.shields.io/github/last-commit/williamervin7/oncology-survival-simulation)
![Methodology](https://img.shields.io/badge/methodology-STROBE%20%7C%20TRIPOD-informational)

# Oncology Survival Analysis & Patient-Level Markov Microsimulation

An applied data science and clinical biostatistics framework for modeling time-to-event oncology data, translating survival estimates into discrete-time transition probabilities, and evaluating how survival-model selection influences downstream patient-level Monte Carlo microsimulation outcomes.

## Research Question

**Does the choice of survival model — Cox Proportional Hazards vs. Random Survival Forest — used to parameterize a Markov microsimulation meaningfully change simulated long-term patient outcomes?**

This project investigates the relationship between machine learning survival-model performance and downstream decision-analytic modeling.

Rather than benchmarking Cox Proportional Hazards (Cox PH) against Random Survival Forests (RSF) using discrimination and calibration metrics alone, the objective is to evaluate whether differences between survival models propagate into materially different simulated patient outcomes when their estimates are used to parameterize a Markov microsimulation.

This question has implications for the development and evaluation of decision-analytic models in healthcare, particularly when survival estimates serve as inputs to longer-term health economic and outcomes research.

**Study population:** Patients diagnosed with Stage III colon cancer using SEER data (2010–2023).

**Primary endpoint:** Overall survival. This endpoint avoids reliance on cause-specific death attribution and provides a consistent basis for comparing Cox PH and RSF survival estimates.

## Project Intent & Scope

The project connects two complementary areas of quantitative healthcare research:

1. **Biostatistical Survival Modeling:** Estimating time-to-event outcomes while accounting for right-censoring, evaluating model assumptions, assessing functional forms, and comparing semi-parametric and machine learning survival approaches.
2. **Health Economics & Outcomes Decision Simulation:** Translating estimated survival functions into discrete-time transition probabilities and evaluating long-term patient trajectories through patient-level microsimulation.

The architecture deliberately separates survival estimation from simulation. This allows the downstream simulation framework to evaluate the consequences of using different survival-model specifications without conflating model development with simulation mechanics.

## Repository Architecture

```text
├── .github/
│   └── workflows/
│       └── ci.yml                    # CI: flake8 lint and pytest
├── data/
│   ├── raw/                          # Original SEER extract (not tracked)
│   └── processed/                    # Filtered and cleaned analysis cohorts
├── documents/
│   ├── articles.md                   # Research literature summaries
│   ├── covariate_selection.md        # Rationale for predefined Cox covariates
│   ├── missingness_audit.md          # Missing-data audit and dispositions
│   └── seer_field_selection_rationale.md
├── Images/                           # Model diagnostic visualizations
├── notebooks/
│   ├── eda.ipynb                     # Exploratory data analysis
│   └── cox_model.ipynb               # Cox PH modeling and refinement
├── results/
│   ├── cox_primary_hazard_ratios.csv # Primary linear Cox model results
│   └── cox_refined_hazard_ratios.csv # Refined spline-model coefficients
├── src/
│   ├── __init__.py
│   ├── config.py                     # Project constants and model configuration
│   ├── data/
│   │   └── cleaning.py               # SEER loading and preprocessing
│   ├── models/
│   │   └── models.py                 # Preprocessing and Cox model utilities
│   ├── simulation/                   # Planned: microsimulation engine
│   └── validation/                    # Planned: calibration and validation
├── tests/
│   ├── software/                     # Software correctness tests
│   └── statistical/                  # Mathematical invariant tests
├── environment.yml                   # Reproducible Conda environment
├── pyproject.toml                    # Project and tooling configuration
├── CHANGELOG.md                      # Version history
└── README.md
```

## Methodology & Reporting Standards

The project draws on established reporting and modeling frameworks to support transparency, reproducibility, and methodological rigor.

- **STROBE:** Guides transparent reporting of the observational cohort, participant selection, variables, and statistical methods.
- **TRIPOD:** Informs transparent reporting of prediction-model development and evaluation.
- **ISPOR-SMDM Modeling Good Research Practices:** Informs the design, documentation, validation, and reporting of the downstream decision-analytic simulation.

These frameworks provide methodological guidance; their inclusion does not imply formal certification or complete compliance.

## Implementation Roadmap

### Phase 1: Semi-Parametric & Non-Parametric Survival Analysis — Model Development and Refinement

The first phase establishes the survival-analysis foundation using the SEER Stage III colon cancer cohort.

Completed work includes:

- Processing survival data while accounting for right-censoring.
- Conducting exploratory data analysis and cohort characterization.
- Implementing Kaplan-Meier survival estimation.
- Fitting multivariable Cox Proportional Hazards models.
- Evaluating proportional hazards assumptions using Schoenfeld residuals.
- Assessing continuous predictor functional forms using Martingale residuals and spline-based comparisons.
- Exploring time-dependent effects for selected Stage indicators.
- Comparing the original linear model with a refined nonlinear specification.
- Exporting model coefficient tables as reproducible results artifacts.

**Current status:** The primary Cox PH model has been fitted, and its diagnostic and refinement workflow has been implemented. The refined model incorporates nonlinear specifications for Age and Regional Nodes Examined. Final diagnostic reassessment, interpretation, and validation remain in progress.

**Cohort:** 14,235 complete-case observations and 6,404 deaths.

#### Preliminary Model Results

| Analysis | Method / Specification | Preliminary Outcome |
|---|---|---|
| Primary Cox PH model | 7 predefined baseline covariates; 13 model terms; Stage IIIA reference | C-index 0.720; Stage IIIB HR 1.85 (95% CI 1.66–2.05); Stage IIIC HR 3.99 (3.58–4.46) |
| PH assumption | `check_assumptions()` with KM and rank transforms; scaled Schoenfeld residuals with LOWESS | Six terms flagged: Age, Regional Nodes Examined, Stage IIIB, Stage IIIC, Married, and Widowed |
| Functional form | Martingale residuals and linear-versus-natural-cubic-spline comparisons | Nonlinearity supported for Age and Regional Nodes Examined; Year of Diagnosis retained as linear |
| Time-dependent Stage effects | Piecewise Cox model with an analyst-selected 12-month cutpoint | Not retained: LR = 1.03, df = 2, p = 0.60; partial AIC higher than the primary model |
| Refined Cox model | Nonlinear spline specifications for Age and Regional Nodes Examined | C-index 0.728; partial AIC decreased from approximately 112,506 to 112,191 |

**Refined-model comparison:** The preliminary likelihood-ratio comparison produced LR = 323.3 with 4 degrees of freedom (p approximately 1.03 × 10⁻⁶⁸). Verification that the spline basis properly nests the original linear specifications remains necessary before treating this as a definitive nested-model test.

#### Current Limitations & Outstanding Work

- Reported concordance and model-fit statistics represent apparent performance on the development cohort. Internal and external validation have not yet been completed.
- Proportional hazards diagnostics were initially performed on the primary linear model. The refined spline model still requires a separate PH reassessment.
- The spline-basis construction and nesting assumptions must be verified before finalizing the likelihood-ratio comparison.
- The 12-month piecewise cutpoint is a modeling choice, not an empirically established clinical threshold. Sensitivity to alternative cutpoints has not been evaluated.
- Individual spline-basis coefficients are not directly interpretable as standalone hazard ratios. Adjusted effect curves will be used to communicate the continuous predictor relationships.
- Hazard ratios represent adjusted associations in observational registry data, not causal effects.

### Phase 2: Machine Learning Extensions & Calibration

The second phase introduces a Random Survival Forest model to evaluate whether a more flexible, non-parametric survival approach produces meaningfully different estimates.

Planned work:

- Implement a Random Survival Forest model.
- Evaluate nonlinear relationships and potential interactions.
- Compare Cox PH and RSF discrimination using the Concordance Index.
- Evaluate prediction error and calibration using time-dependent Brier Scores.
- Assess performance across relevant follow-up intervals.
- Perform internal validation to evaluate model stability and reduce optimism in apparent performance.
- Compare estimated survival functions across modeling approaches.

The objective is not simply to identify the model with the highest predictive performance, but to characterize how differences in estimated survival translate into downstream simulation inputs.

### Phase 3: Mathematical Derivation & Markov Transition Modeling

The third phase translates survival estimates into discrete-time transition probabilities and establishes the mathematical foundation for the microsimulation.

Planned work:

- Derive discrete-time transition probabilities from estimated survival functions.
- Define health states and permissible transitions based on available data and clearly documented assumptions.
- Establish cycle length and apply half-cycle corrections where appropriate.
- Evaluate probability constraints and ensure transition probabilities remain valid.
- Implement structural validation and mathematical invariant checks.

**State structure consideration:** Overall survival directly supports modeling transitions between alive and dead states. More detailed states, such as stable disease and progression, will require appropriate progression data or separately justified transition assumptions. These states will not be inferred from overall survival alone.

### Phase 4: Patient-Level Monte Carlo Microsimulation

The final phase implements a patient-level simulation engine to evaluate long-term outcomes under alternative survival-model parameterizations.

Planned work:

- Construct a vectorized patient-level Monte Carlo simulation engine.
- Implement a centralized, reproducible random number generation framework.
- Simulate individual patient trajectories across defined health states.
- Run repeated Monte Carlo iterations to characterize outcome variability.
- Compare simulated outcomes using Cox PH-derived and RSF-derived survival estimates.
- Evaluate whether differences in survival-model selection produce materially different aggregate and patient-level outcomes.
- Perform structural validation by comparing simulated aggregate survival patterns against empirical Kaplan-Meier estimates where the model structure permits.

The ultimate objective is to determine whether the choice of survival model has meaningful consequences beyond conventional predictive performance metrics when used within a downstream decision-analytic framework.

## Reproducibility

The project uses a version-controlled Python environment and automated testing workflow to support reproducible analysis.

- Conda environment specification maintained in `environment.yml`.
- Project configuration and shared constants maintained in `src/config.py`.
- Automated linting and software tests through GitHub Actions.
- Statistical tests designed to evaluate mathematical properties and model invariants.
- Model results exported to the `results/` directory.
- Raw SEER data are not included in the repository; users must obtain the appropriate data access and generate the required extract independently.

## Project Direction

This project is designed to progress from foundational survival analysis into machine learning, statistical calibration, and patient-level simulation.

The central objective is to connect statistical modeling decisions with their downstream implications for healthcare decision analysis. By evaluating how alternative survival-model estimates influence simulated patient outcomes, the project aims to provide a more complete understanding of the role model selection plays in computational oncology and health outcomes research.