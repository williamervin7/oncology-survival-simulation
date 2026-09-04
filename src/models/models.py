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
    
    
def univariate_model(df, duration_col, event_col, covariate):
    cph = CoxPHFitter()
    cph.fit(df[[duration_col, event_col, covariate]], duration_col=duration_col, event_col=event_col)
    return cph

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
    result = univariate_model(df_clean, duration_col='Time', event_col='Event', covariate='Age recode with single ages and 90+')
    result.print_summary()

    