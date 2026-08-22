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
    # Add cleaning steps here
    return df