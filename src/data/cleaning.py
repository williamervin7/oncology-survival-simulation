import numpy as np
import pandas as pd
import os 
from pathlib import Path

def get_data():
    # Anchored to this file's location, not the process's working directory.
    # src/data/cleaning.py -> parents[2] -> repo root
    BASE_DIR = Path(__file__).resolve().parents[2]
    data_folder = BASE_DIR / "data"
    file = data_folder / "raw" / "raw_data.csv"
    df = pd.read_csv(file)
    print("Data loaded successfully.")
    print(f"Raw data shape: {df.shape}")
    return df


def convert_missing_values(df):
    # 1. Convert SEER-specific missing string patterns to standard NaN
    missing_patterns = ["Blank(s)", "Unknown", "999", "9999"]
    df_clean = df.replace(missing_patterns, np.nan)

    # 2. Derive binary event flag (overall survival) and coerce survival time to numeric
    df_clean["Time"] = pd.to_numeric(df_clean["Survival months"], errors="coerce")
    df_clean["Event"] = np.where(
        df_clean["Vital status recode (study cutoff used)"] == "Dead",
        1,
        0,    )
    # 3. Explicitly drop rows missing core outcome metrics (Time or Event)
    df_clean = df_clean.dropna(subset=["Time", "Event"])
    return df_clean

def derive_stage_2018(df):
    """
    Primary Stage derivation for 2018+ from SEER's pre-derived
    'Derived EOD 2018 Stage Group Recode (2018+)' field, confirmed via SEER
    EOD 2018 training documentation as a direct AJCC 8th edition TNM Stage
    Group derivation (not a related-but-distinct concept).
    """
    raw_col = "Derived EOD 2018 Stage Group Recode (2018+)"
    stage_map = {
        "0": "0",
        "1": "I",
        "2A": "IIA", "2B": "IIB", "2C": "IIC",
        "2": "II",   # confirmed Stage II, substage unknown
        "3": "III",  # confirmed Stage III, substage unknown
        "4": "IV",   # confirmed Stage IV, substage unknown
        "3A": "IIIA", "3B": "IIIB", "3C": "IIIC",
        "4A": "IVA", "4B": "IVB", "4C": "IVC",
        "88": np.nan,
    }
    is_2018_plus = df["Year of diagnosis"] >= 2018

    df["2018+_Stage"] = None
    df.loc[is_2018_plus, "2018+_Stage"] = (
        df.loc[is_2018_plus, raw_col].astype(str).str.strip().map(stage_map)
    )
    return df

def derive_stage_2018_tnm_validation(df):
    """
    Derive AJCC 8th edition Stage Group for diagnosis years 2018+ from the
    'Derived EOD 2018 T/N/M Recode (2018+)' fields, using the stage-grouping
    tables sourced from PDQ/NCI (Tables 3, 4, and 5 -- see articles.md),
    confirmed identical to AJCC 7th edition for colon cancer via the AJCC
    Hindgut Taskforce validation (PMC2815715).

    Mapping rules (AJCC 8th ed., colon and rectum):
        Stage 0:    Tis, N0, M0
        Stage I:    T1-T2, N0, M0
        Stage IIA:  T3, N0, M0
        Stage IIB:  T4a, N0, M0
        Stage IIC:  T4b, N0, M0
        Stage IIIA: T1-T2, N1, M0  or  T1, N2a, M0
        Stage IIIB: T3-T4a, N1, M0  or  T2-T3, N2a, M0  or  T1-T2, N2b, M0
        Stage IIIC: T4a, N2a, M0  or  T3-T4a, N2b, M0  or  T4b, N1-N2, M0
        Stage IVA:  Any T, Any N, M1a
        Stage IVB:  Any T, Any N, M1b
        Stage IVC:  Any T, Any N, M1c

    Handling decisions (documented in seer_field_selection_rationale.md):
        - T1a/T1b collapsed to T1; T2a/T2b collapsed to T2. The stage
          tables only distinguish at the T1/T2/T3/T4a/T4b level, so these
          sub-splits don't affect stage placement.
        - N1a/N1b/N1c collapsed to N1. All N1 subtypes map identically
          across every stage boundary in the tables above (confirmed by
          the tables' own "N1/N1c" notation for IIIA/IIIB).
        - Rows with unresolvable ambiguity are assigned Stage = NaN rather
          than guessed:
            * bare 'T4' (a/b not specified) -- can't distinguish IIB/IIC
              or IIIB/IIIC boundaries that depend on a vs. b
            * bare 'N2' combined with T2 or T3 -- IIIB vs. IIIC depends on
              N2a vs. N2b in that specific T range
            * bare 'M1' (a/b/c not specified) -- can't distinguish
              IVA/IVB/IVC, which are defined entirely by the M sub-code
        - TX, NX, and code 88 ("not applicable," confirmed via SEER EOD
          2018 General Coding Instructions) all map to NaN, consistent
          with their AJCC/SEER definitions.

    Only rows with Year of diagnosis >= 2018 are touched. All other rows
    are left with Stage = NaN, for safe combination with the 2010-2015 and
    2016-2017 stage derivations later.
    """
    t_col = "Derived EOD 2018 T Recode (2018+)"
    n_col = "Derived EOD 2018 N Recode (2018+)"
    m_col = "Derived EOD 2018 M Recode (2018+)"

    is_2018_plus = df["Year of diagnosis"] >= 2018

    t_raw = df.loc[is_2018_plus, t_col].astype(str).str.strip()
    n_raw = df.loc[is_2018_plus, n_col].astype(str).str.strip()
    m_raw = df.loc[is_2018_plus, m_col].astype(str).str.strip()

    # --- Normalize T: collapse sub-splits, drop unresolvable/inapplicable codes ---
    t_map = {
        "Tis": "Tis", "Tis(LAMN)": "Tis",
        "T0": "T0",
        "T1": "T1", "T1a": "T1", "T1b": "T1",
        "T2": "T2", "T2a": "T2", "T2b": "T2",
        "T3": "T3",
        "T4a": "T4a",
        "T4b": "T4b",
        # TX, bare "T4", "T4c", and "88" are intentionally NOT mapped -> NaN
    }
    t_norm = t_raw.map(t_map)

    # --- Normalize N: collapse N1 sub-splits, drop unresolvable/inapplicable codes ---
    n_map = {
        "N0": "N0",
        "N1": "N1", "N1a": "N1", "N1b": "N1", "N1c": "N1",
        "N2a": "N2a",
        "N2b": "N2b",
        # NX, bare "N2", and "88" are intentionally NOT mapped -> NaN
    }
    n_norm = n_raw.map(n_map)

    # --- Normalize M: keep sub-codes distinct, drop unresolvable/inapplicable codes ---
    m_map = {
        "M0": "M0",
        "M1a": "M1a",
        "M1b": "M1b",
        "M1c": "M1c",
        # bare "M1", MX, and "88" are intentionally NOT mapped -> NaN
    }
    m_norm = m_raw.map(m_map)

    # --- Apply AJCC 8th ed. stage grouping rules (Tables 3, 4, 5) ---
    conditions = [
        m_norm == "M1a",
        m_norm == "M1b",
        m_norm == "M1c",
        (m_norm == "M0") & (t_norm == "Tis") & (n_norm == "N0"),
        (m_norm == "M0") & (t_norm.isin(["T1", "T2"])) & (n_norm == "N0"),
        (m_norm == "M0") & (t_norm == "T3") & (n_norm == "N0"),
        (m_norm == "M0") & (t_norm == "T4a") & (n_norm == "N0"),
        (m_norm == "M0") & (t_norm == "T4b") & (n_norm == "N0"),
        (m_norm == "M0") & (t_norm.isin(["T1", "T2"])) & (n_norm == "N1"),
        (m_norm == "M0") & (t_norm == "T1") & (n_norm == "N2a"),
        (m_norm == "M0") & (t_norm.isin(["T3", "T4a"])) & (n_norm == "N1"),
        (m_norm == "M0") & (t_norm.isin(["T2", "T3"])) & (n_norm == "N2a"),
        (m_norm == "M0") & (t_norm.isin(["T1", "T2"])) & (n_norm == "N2b"),
        (m_norm == "M0") & (t_norm == "T4a") & (n_norm == "N2a"),
        (m_norm == "M0") & (t_norm.isin(["T3", "T4a"])) & (n_norm == "N2b"),
        (m_norm == "M0") & (t_norm == "T4b") & (n_norm.isin(["N1", "N2a", "N2b"])),
    ]
    choices = [
        "IVA", "IVB", "IVC",
        "0",
        "I",
        "IIA", "IIB", "IIC",
        "IIIA", "IIIA",
        "IIIB", "IIIB", "IIIB",
        "IIIC", "IIIC", "IIIC",
    ]

    stage = np.select(conditions, choices, default="UNSTAGED")
    stage = pd.Series(stage, index=t_raw.index).replace("UNSTAGED", np.nan)

    df["2018+_Stage"] = None  # Initialize 2018+_Stage column with NaN
    df.loc[is_2018_plus, "2018+_Stage"] = stage

    # Transparency check: report staging yield rather than letting
    # unstageable rows disappear silently
    n_total = is_2018_plus.sum()
    n_unstaged = df.loc[is_2018_plus, "2018+_Stage"].isna().sum()
    print(
        f"2018+ Stage derivation: {n_total - n_unstaged}/{n_total} rows staged "
        f"({n_unstaged} unstageable: TX/NX/MX, code 88, T0, or unresolved sub-split ambiguity)"
    )

    return df


def consolidate_stage(df):
    """
    Consolidate stage information from multiple year-specific derivations into a single Stage column.
    
    Priority order (highest to lowest):
        1. 2018+_Stage (AJCC 8th edition, most recent)
        2. Derived AJCC Stage Group, 7th ed (2010-2015)
        3. 7th Edition Stage Group Recode (2016-2017)
    
    Takes the first non-null/non-NaN value encountered in the priority order.
    """
    col_2018_plus = "2018+_Stage"
    col_7ed_2010_2015 = "Derived AJCC Stage Group, 7th ed (2010-2015)"
    col_7ed_2016_2017 = "7th Edition Stage Group Recode (2016-2017)"

    overlap = df[[col_2018_plus, col_7ed_2010_2015, col_7ed_2016_2017]].notna().sum(axis=1)
    n_overlapping = (overlap > 1).sum()
    print(f"Rows with more than one stage source populated: {n_overlapping}")

    df["Stage"] = df[col_2018_plus].fillna(
        df[col_7ed_2010_2015].fillna(df[col_7ed_2016_2017])
    )
    
    # Transparency check: report stage consolidation results
    n_total = len(df)
    n_staged = df["Stage"].notna().sum()
    n_unstaged = df["Stage"].isna().sum()
    print(
        f"Stage consolidation: {n_staged}/{n_total} rows have stage information "
        f"({n_unstaged} unstaged)"
    )
    
    return df

def get_stage_III(df):
    """
    Filter the dataframe to include only rows with Stage IIIA, IIIB, IIIC, III or IIINOS.
    """
    return df[df["Stage"].isin(["IIIA", "IIIB", "IIIC", "III", "IIINOS"])]

def save_cleaned_data(df, filename="cleaned_data.csv"):
    """
    Save the cleaned dataframe to a CSV file in the 'data/processed' directory.
    """
    BASE_DIR = Path(__file__).resolve().parents[2]
    processed_folder = BASE_DIR / "data" / "processed"
    processed_folder.mkdir(parents=True, exist_ok=True)
    file_path = processed_folder / filename
    df.to_csv(file_path, index=False)
    print(f"Cleaned data saved to {file_path}")

def clean_process():
    """
    Run the full data cleaning and transformation process, including:
    1. Loading raw data
    2. Converting missing values
    3. Deriving stage for 2018+ cases
    4. Consolidating stage information
    5. Filtering to Stage III cases
    """
    print("Running data cleaning and transformation functions...")
    df = get_data()
    df_clean = convert_missing_values(df)
    print(f"Missing values converted")
    df_clean = derive_stage_2018(df_clean)
    print(f"Stage derived for 2018+ cases")
    print(df_clean.loc[df_clean['Year of diagnosis'] >= 2018, '2018+_Stage'].value_counts(dropna=False))
    df_clean = consolidate_stage(df_clean)
    print(f"\nConsolidated stage column created")
    print(df_clean['Stage'].value_counts(dropna=False))
    df_clean = get_stage_III(df_clean)
    print(f"\nFiltered to Stage III cases")
    print(df_clean['Stage'].value_counts(dropna=False))
    return df_clean


if __name__ == "__main__":
   clean_process()
    