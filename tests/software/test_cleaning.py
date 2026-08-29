import pytest
import numpy as np
import pandas as pd
from src.data.cleaning import convert_missing_values, derive_stage_2018, consolidate_stage, get_stage_III, event_flag

def test_convert_missing_values():
    df = pd.DataFrame({
        "col1": ["NA", "N/A", "na", "n/a", "missing", "Missing", "MISSING", "valid"],
        "col2": [1, 2, 3, 4, 5, 6, 7, 8]
    })

    result = convert_missing_values(df)

    # Check that the known missing value representations are converted to NaN
    assert pd.isna(result["col1"].iloc[0])
    assert pd.isna(result["col1"].iloc[1])
    assert pd.isna(result["col1"].iloc[2])
    assert pd.isna(result["col1"].iloc[3])
    assert pd.isna(result["col1"].iloc[4])
    assert pd.isna(result["col1"].iloc[5])
    assert pd.isna(result["col1"].iloc[6])
    # Check that valid values remain unchanged
    assert result["col1"].iloc[7] == "valid"

def test_event_flag():
    df = pd.DataFrame({
        "Survival months": ["12", "24", "36", "48", "60", "invalid"],
        "Vital status recode (study cutoff used)": ["Dead", "Alive", "Dead", "Alive", "Dead", "Dead"]
    })
    result = event_flag(df)
    # Check that the event flag is correctly derived
    assert result["Event flag"].iloc[0] == 1
    assert result["Event flag"].iloc[1] == 0
    assert result["Event flag"].iloc[2] == 1
    assert result["Event flag"].iloc[3] == 0
    assert result["Event flag"].iloc[4] == 1
    assert result["Event flag"].iloc[5] == 1

    # Check that the survival months are correctly coerced to numeric, with invalid entries converted to NaN
    assert result["Survival months"].iloc[0] == 12
    assert result["Survival months"].iloc[1] == 24
    assert result["Survival months"].iloc[2] == 36
    assert result["Survival months"].iloc[3] == 48
    assert result["Survival months"].iloc[4] == 60
    assert result["Survival months"].iloc[5] == np.nan

# after implementing the cleaning functions this test will check if the shape of the cleaned dataframe is as expected
def test_derive_stage_2018():
    df = pd.DataFrame({
        "Year of diagnosis": [2018, 2018, 2018, 2019, 2015],
        "Derived EOD 2018 Stage Group Recode (2018+)": ["1", "3B", "88", " 2A ", "3B"],
    })

    result = derive_stage_2018(df)

    # known codes map correctly
    assert result["2018+_Stage"].iloc[0] == "I"
    assert result["2018+_Stage"].iloc[1] == "IIIB"
    # code 88 ("not applicable") maps to NaN, not passed through
    assert pd.isna(result["2018+_Stage"].iloc[2])
    # whitespace is stripped before mapping
    assert result["2018+_Stage"].iloc[3] == "IIA"
    # pre-2018 rows are untouched (stay at initialized None), regardless of raw value
    assert result["2018+_Stage"].iloc[4] is None


def test_consolidate_stage():
    df = pd.DataFrame({
        "2018+_Stage":                                       ["IVA", np.nan, np.nan],
        "Derived AJCC Stage Group, 7th ed (2010-2015)":       ["IIIA", "IIB", np.nan],
        "7th Edition Stage Group Recode (2016-2017)":         ["I", "I", np.nan],
    })

    result = consolidate_stage(df)

    # 2018+_Stage wins when populated, even if other sources also have values
    assert result["Stage"].iloc[0] == "IVA"
    # falls back to 2010-2015 source when 2018+_Stage is NaN
    assert result["Stage"].iloc[1] == "IIB"
    # NaN when no source is populated
    assert pd.isna(result["Stage"].iloc[2])
    assert result["Stage"].notna().sum() == 2

def test_get_stage_III():
    # Create a sample dataframe with various stages
    data = {
        "Stage": ["IIIA", "IIIB", "IIIC", "III", "IIINOS", "I", "IV", np.nan]
    }
    df = pd.DataFrame(data)

    # Call the get_stage_III function
    df_stage_III = get_stage_III(df)

    # Check if the resulting dataframe only contains Stage III cases
    expected_stages = ["IIIA", "IIIB", "IIIC", "III", "IIINOS"]
    assert all(stage in expected_stages for stage in df_stage_III["Stage"].unique())
    assert len(df_stage_III) == 5  # There should be 5 rows corresponding to Stage III cases
    



