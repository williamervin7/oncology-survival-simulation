import numpy as np
import pandas as pd
import os 


def get_data():

    BASE_DIR = os.path.dirname(os.getcwd()) # Gets the root project directory
    data_folder = os.path.join(BASE_DIR, "data")
    file = os.path.join(data_folder, "raw", "raw_data.csv")
    df = pd.read_csv(file)
    print("Data loaded successfully.")
    print(f"Raw data shape: {df.shape}")
    return df


def convert_missing_values(df):
    # 1. Convert SEER-specific missing string patterns to standard NaN
    missing_patterns = ["Blank(s)", "Unknown", "999", "9999", "99"]
    df_clean = df.replace(missing_patterns, np.nan)

    # 2. Derive binary event flag (overall survival) and coerce survival time to numeric
    df_clean["Time"] = pd.to_numeric(df_clean["Survival months"], errors="coerce")
    df_clean["Event"] = np.where(
        df_clean["Vital status recode (study cutoff used)"] == "Dead",
        1,
        0,
    )
    # 3. Explicitly drop rows missing core outcome metrics (Time or Event)
    df_clean = df_clean.dropna(subset=["Time", "Event"])
    return df_clean