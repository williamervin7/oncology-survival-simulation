import pytest
import numpy as np
import pandas as pd
import sys
from pathlib import Path

# tests/software/test_cleaing.py -> parents[1] is 'tests', parents[2] is project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from src.data.cleaning import convert_missing_values, derive_stage_2018, consolidate_stage, get_stage_III, event_flag, convert_cols
from src.models.models import preprocessing

def test_convert_missing_values():
    df = pd.DataFrame({
        "col1": ["Blank(s)", "Unknown", "999", "Unknown", "9999", "Blank(s)", "9999", "valid"],
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

    # Row 5 has unparseable Survival months ("invalid" -> NaN via pd.to_numeric),
    # so it should be dropped entirely by dropna(subset=["Time", "Event"]).
    assert len(result) == 5

    # Remaining rows (0-4) should have correctly derived Event and Time
    assert list(result["Event"]) == [1, 0, 1, 0, 1]
    assert list(result["Time"]) == [12, 24, 36, 48, 60]

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
    

def test_convert_cols():
    df = pd.DataFrame({
        "Age recode with single ages and 90+": [
            "001 years", "005 years", "010 years", "90+ years", "invalid", np.nan
        ]
    })

    result = convert_cols(df)
    col = result["Age recode with single ages and 90+"]

    assert col.iloc[0] == 1
    assert col.iloc[1] == 5
    assert col.iloc[2] == 10
    assert col.iloc[3] == 90
    assert pd.isna(col.iloc[4])   # unparseable text
    assert pd.isna(col.iloc[5])   # genuinely missing input
    assert col.dtype == "float64"


def test_preprocessing_encodes_covariates():
    df = pd.DataFrame({
        "Sex": ["Female", "Male", "Female"],
        "Chemotherapy recode (yes, no/unk)": ["Yes", "No/Unknown", "Yes"],
        "Stage": ["IIIA", "IIIB", "IIIC"],
    })

    with pytest.raises(AssertionError):
        preprocessing(df)
    result = preprocessing(df)

    assert list(result["Sex"]) == [0, 1, 0]
    assert list(result["Chemotherapy recode (yes, no/unk)"]) == [1, 0, 1]
    assert "Stage_IIIA" not in result.columns   # dropped as reference category]
    assert list(result["Stage_IIIB"]) == [0, 1, 0]
    assert list(result["Stage_IIIC"]) == [0, 0, 1]
    assert "Stage" not in result.columns
    assert all(pd.api.types.is_integer_dtype(dt) for dt in result[["Stage_IIIC", "Stage_IIIB"]].dtypes)
    assert list(df["Sex"]) == ["Female", "Male", "Female"]

