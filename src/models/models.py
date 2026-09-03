import numpy as np
import pandas as pd
import sys
from pathlib import Path

# src/models/models.py -> parents[1] is 'src', parents[2] is project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Now Python can find 'src' regardless of execution context
from src.config import PROJECT_ROOT, STAGE_THREE_CODES, STAGE_THREE_SIZE
from  src.data.cleaning import get_clean_data

def final_clean():
    print("test")
    df = get_clean_data()
    unknowns = ['Regional nodes examined (1988+)', 'Regional nodes positive (1988+)', 'Rx Summ--Surg Prim Site (1998-2022)']
    df_clean = df.replace(unknowns, np.nan)
    print(f"Missing values replaced with NaN in columns: {unknowns}")
    return df_clean
    
    





if __name__ == "__main__":
    df = final_clean()

    