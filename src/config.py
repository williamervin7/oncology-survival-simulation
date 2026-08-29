# src/config.py
from pathlib import Path

# Project-wide global variables & constants
RANDOM_SEED = 42
DEFAULT_TIME_HORIZON = 120  # months
STAGE_THREE_CODES = ["IIIA", "IIIB", "IIIC", "III", "IIINOS"]
STAGE_THREE_SIZE = 14443 #verified with the cleaned dataset after filtering for Stage III cases

# Dynamically set project root path relative to this config file
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"