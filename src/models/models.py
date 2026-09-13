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
from src.config import PROJECT_ROOT, STAGE_THREE_CODES, STAGE_THREE_SIZE
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

def univariate_model(df, duration_col, event_col, covariate):
    cph = CoxPHFitter()
    cph.fit(df[[duration_col, event_col, covariate]], duration_col=duration_col, event_col=event_col)
    return cph

def preprocessing(df):
    """Prepare baseline covariates for the primary Cox PH model.

    Primary Cox PH covariates:
        - Age
        - Sex
        - Stage (IIIA reference; IIIB and IIIC indicators)
        - Marital status
        - Race
        - Regional nodes examined
        - Year of diagnosis

    Chemotherapy is intentionally excluded because it is a post-diagnosis
    treatment variable rather than a baseline covariate.
    """
    df_processed = df.copy()
    # ------------------------------------------------------------------
    # Define primary Cox PH model columns
    # ------------------------------------------------------------------
    cox_cols = [
        "Age recode with single ages and 90+",
        "Sex",
        "Stage",
        "Marital status at diagnosis",
        "Race recode (White, Black, Other)",
        "Regional nodes examined (1988+)",
        "Year of diagnosis",
    ]

    df_processed = df_processed[cox_cols].copy()

    # ------------------------------------------------------------------
    # Sex: binary encoding
    # ------------------------------------------------------------------
    assert df_processed["Sex"].isin(["Female", "Male"]).all(), (
        "Unexpected value in Sex"
    )

    df_processed["Sex"] = df_processed["Sex"].map(
        {"Female": 0, "Male": 1}
    )

    # ------------------------------------------------------------------
    # Stage: IIIA reference
    # ------------------------------------------------------------------
    expected_stage = {"IIIA", "IIIB", "IIIC"}

    assert set(df_processed["Stage"].unique()).issubset(expected_stage), (
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
    # ------------------------------------------------------------------
     # get dummies for marital status and race, dropping the first category to avoid multicollinearity
    # ------------------------------------------------------------------
    marital_dummies = pd.get_dummies(
        df_processed["Marital status at diagnosis"],
        prefix="Marital",
        dtype=int,
        drop_first=True,
    )

    df_processed = pd.concat(
    [
        df_processed.drop(columns="Marital status at diagnosis"),
        marital_dummies,
    ],
    axis=1,
    )

    race_dummies = pd.get_dummies(
        df_processed["Race recode (White, Black, Other)"],
        prefix="Race",
        dtype=int,
        drop_first=True,
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

if __name__ == "__main__":
    df_clean = resolve_special_codes()
    df_clean = remove_unspecified_stage_III(df_clean)
    df_encoded = preprocessing(df_clean)
    print("***************")
    print(df_encoded.columns.tolist())
    
    """print(df_clean[["Stage"]].value_counts())
    result = run_univariate_screen(df_encoded, duration_col='Time', event_col='Event', covariates=[
        'Age recode with single ages and 90+',
        'Sex',
        'Chemotherapy recode (yes, no/unk)',
        'Stage_IIIB',   # not 'Stage' — it no longer exists as one column
        'Stage_IIIC',
    ],)
    print(result)"""


    