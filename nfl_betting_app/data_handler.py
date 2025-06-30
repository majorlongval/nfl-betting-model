import pandas as pd
import os
import nfl_betting_app.config as config

# Specifying dtypes helps pandas read the large CSV much faster and use less memory.
PBP_DTYPE_MAP = {
    'game_id': 'str',
    'home_team': 'str',
    'away_team': 'str',
    'posteam': 'str',
    'season_type': 'str',
    'week': 'int',
    'down': 'float',  # Float to handle potential NaNs
    'third_down_converted': 'float',
    'third_down_failed': 'float',
    'fourth_down_converted': 'float',
    'fourth_down_failed': 'float',
    'rushing_yards': 'float',
    'passing_yards': 'float',
    'pass_touchdown': 'float',
    'rush_touchdown': 'float',
    'return_touchdown': 'float',
    'interception': 'float',
    'fumble_lost': 'float',
    'td_team': 'str',
    'td_player_name': 'str',
    'spread_line': 'float',
    'total_line': 'float',
    'result': 'float'
}

def load_raw_pbp_data() -> pd.DataFrame:
    """
    Loads the raw play-by-play database from the local raw data folder.
    Raises FileNotFoundError if the database does not exist.
    """
    # Prioritize loading the much faster Parquet file if it exists.
    if os.path.exists(config.RAW_PBP_PARQUET_PATH):
        print("Loading raw play-by-play data from local Parquet file (fast)...")
        return pd.read_parquet(config.RAW_PBP_PARQUET_PATH)

    # Fallback to CSV if Parquet file is not found.
    elif os.path.exists(config.RAW_PBP_DB_PATH):
        print("Loading raw play-by-play data from local CSV...")
        print("(This may take a minute. Run data_retriever.py to generate a faster Parquet file.)")
        return pd.read_csv(config.RAW_PBP_DB_PATH, dtype=PBP_DTYPE_MAP, low_memory=False)

    else:
        raise FileNotFoundError(
            f"ERROR: Raw PBP database not found at '{config.RAW_PBP_DB_PATH}'. "
            "Please run the data_retriever.py script first to create it."
        )
