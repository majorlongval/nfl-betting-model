import pandas as pd
import os
import nfl_betting_app.config as config

def load_raw_pbp_data() -> pd.DataFrame:
    """
    Loads the raw play-by-play database from the local raw data folder.
    Raises FileNotFoundError if the database does not exist.
    """
    if not os.path.exists(config.RAW_PBP_DB_PATH):
        raise FileNotFoundError(
            f"ERROR: Raw PBP database not found at '{config.RAW_PBP_DB_PATH}'. "
            "Please run the data_retriever.py script first to create it."
        )

    print("Loading raw play-by-play data from local CSV...")
    return pd.read_csv(config.RAW_PBP_DB_PATH, low_memory=False)
