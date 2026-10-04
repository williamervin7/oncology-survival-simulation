import numpy as np
import pandas as pd
import sys
from pathlib import Path
from lifelines import CoxPHFitter


# src/models/models.py -> parents[1] is 'src', parents[2] is project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Now Python can find 'src' regardless of execution context
from src.config import PROJECT_ROOT, STAGE_THREE_CODES, STAGE_THREE_SIZE, COX_COVARIATES
from  src.data.cleaning import get_clean_data

def resolve_special_codes():
    """
    Recodes SEER field-specific 'unknown' sentinel values to NaN.

    Only code 99 is treated as missing in these columns. Values like 9 or 88
    in the node-count fields are legitimate exact counts (SEER allows 01-89
    as real node counts), not missing-value codes — confirmed against SEER
    Program field descriptions. See missingness_audit.md for full disposition
    of all 36 columns.

    Columns handled:
    - Regional nodes examined (1988+): 99 = unknown whether nodes removed
    - Regional nodes positive (1988+): 99 = unknown whether nodes positive
    - Rx Summ--Surg Prim Site (1998-2022): 99 = unknown/not stated
    """
    df = get_clean_data()
    cols = [
        'Regional nodes examined (1988+)',
        'Regional nodes positive (1988+)',
        'RX Summ--Surg Prim Site (1998-2022)',
    ]

    df_clean = df.copy()
    df_clean[cols] = df_clean[cols].replace(99, np.nan)

    print(f"Recoded 99 -> NaN in: {cols}")
    return df_clean
    
def remove_unspecified_stage_III(df):
    """
    Removes rows with Stage III or IIINOS
    """    
    return df[~df["Stage"].isin(["III", "IIINOS"])]

def preprocess_for_modeling():
    """
    Prepares the cleaned dataset for modeling by resolving special codes and
    removing unspecified Stage III cases.
    """
    df_clean = resolve_special_codes()
    df_clean = remove_unspecified_stage_III(df_clean)
    return df_clean

def univariate_model(df, duration_col, event_col, covariate):
    cph = CoxPHFitter()
    cph.fit(df[[duration_col, event_col, covariate]], duration_col=duration_col, event_col=event_col)
    return cph

def preprocessing(df):
    """Prepare baseline covariates for the primary Cox PH model.

    Primary Cox PH covariates:
        - Age
        - Sex (Female reference)
        - Stage (IIIA reference; IIIB and IIIC indicators)
        - Marital status (Single [never married] reference)
        - Race (Black reference)
        - Regional nodes examined
        - Year of diagnosis

    Chemotherapy is intentionally excluded because it is a post-diagnosis
    treatment variable rather than a baseline covariate.
    """
    df_processed = df.copy()

    # Define primary Cox PH model columns
    cox_cols = COX_COVARIATES
    df_processed = df_processed[cox_cols].copy()

    # Sex: Female reference
    expected_sex = {"Female", "Male"}

    assert df_processed["Sex"].isin(expected_sex).all(), (
        "Unexpected value in Sex"
    )

    # Female = 0 (reference), Male = 1
    df_processed["Sex"] = df_processed["Sex"].map(
        {"Female": 0, "Male": 1}
    )

    # Stage: IIIA reference
    expected_stage = {"IIIA", "IIIB", "IIIC"}

    assert df_processed["Stage"].isin(expected_stage).all(), (
        "Unexpected value in Stage"
    )

    stage_dummies = pd.get_dummies(
        df_processed["Stage"],
        prefix="Stage",
        dtype=int,
        drop_first=False,
    )

    # Explicitly retain IIIA as reference and create indicators
    # for IIIB and IIIC.
    stage_dummies = stage_dummies[
        ["Stage_IIIB", "Stage_IIIC"]
    ]

    df_processed = pd.concat(
        [
            df_processed.drop(columns="Stage"),
            stage_dummies,
        ],
        axis=1,
    )

    # Marital status: Single (never married) reference
    expected_marital = set(df_processed["Marital status at diagnosis"].unique())

    assert "Single (never married)" in expected_marital, (
        "Reference category 'Single (never married)' not found in Marital status"
    )

    marital_dummies = pd.get_dummies(
        df_processed["Marital status at diagnosis"],
        prefix="Marital",
        dtype=int,
        drop_first=False,
    )

    # Explicitly use Single (never married) as reference
    marital_dummies = marital_dummies.drop(
        columns="Marital_Single (never married)"
    )

    df_processed = pd.concat(
        [
            df_processed.drop(columns="Marital status at diagnosis"),
            marital_dummies,
        ],
        axis=1,
    )

    # Race: Black reference
    expected_race = set(
        df_processed["Race recode (White, Black, Other)"].unique()
    )

    assert "Black" in expected_race, (
        "Reference category 'Black' not found in Race"
    )

    race_dummies = pd.get_dummies(
        df_processed["Race recode (White, Black, Other)"],
        prefix="Race",
        dtype=int,
        drop_first=False,
    )

    # Explicitly use Black as reference
    race_dummies = race_dummies.drop(
        columns="Race_Black"
    )

    df_processed = pd.concat(
        [
            df_processed.drop(columns="Race recode (White, Black, Other)"),
            race_dummies,
        ],
        axis=1,
    )

    return df_processed

def run_univariate_screen(df, duration_col, event_col, covariates):
    """
    Fits a separate univariate Cox PH model for each candidate covariate.
    For reporting/comparison purposes only — NOT used to filter which
    covariates enter the multivariable model (see TRIPOD note in
    modeling.ipynb / project notes on avoiding univariate selection bias).
    """
    results = []
    for cov in covariates:
        cols = [duration_col, event_col] + (cov if isinstance(cov, list) else [cov])
        sub = df[cols].dropna()
        cph = CoxPHFitter()
        cph.fit(sub, duration_col=duration_col, event_col=event_col)
        summary = cph.summary
        summary['covariate_group'] = cov if isinstance(cov, str) else '+'.join(cov)
        summary['n_obs'] = len(sub)
        results.append(summary)
    return pd.concat(results)

def run_multivariable_model(df, duration_col, event_col):
    """Fits a multivariable Cox PH model with the specified covariates."""

    cph = CoxPHFitter()

    df_processed = preprocessing(df)

    run_df = pd.concat(
        [
            df[[duration_col, event_col]],
            df_processed,
        ],
        axis=1,
    ).dropna()

    cph.fit(
        run_df,
        duration_col=duration_col,
        event_col=event_col,
    )

    return cph
if __name__ == "__main__":
    df_clean = preprocess_for_modeling()
    df_cph = run_multivariable_model(df_clean, duration_col='Time', event_col='Event')
    #print(df_cph.summary)
    df_cph.print_summary()



    