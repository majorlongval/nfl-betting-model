import pandas as pd
import os
import nfl_betting_app.config as config


def load_raw_game_data() -> pd.DataFrame:
    """
    Loads the raw games and odds database from the local raw data folder.
    Raises FileNotFoundError if the database does not exist.
    """
    if not os.path.exists(config.RAW_GAMES_DB_PATH):
        raise FileNotFoundError(
            f"ERROR: Raw games database not found at '{config.RAW_GAMES_DB_PATH}'. "
            "Please run the data_retriever.py script first to create it."
        )

    print("Loading raw games database from local CSV...")
    return pd.read_csv(config.RAW_GAMES_DB_PATH, low_memory=False)


def load_raw_weekly_player_stats_data() -> pd.DataFrame:
    """
    Loads the raw weekly player stats database from the local raw data folder.
    Raises FileNotFoundError if the database does not exist.
    """
    if not os.path.exists(config.RAW_STATS_DB_PATH):
        raise FileNotFoundError(
            f"ERROR: Raw weekly player stats database not found at '{config.RAW_STATS_DB_PATH}'. "
            "Please run the data_retriever.py script first to create it."
        )

    print("Loading raw weekly player stats from local CSV...")
    return pd.read_csv(config.RAW_STATS_DB_PATH, low_memory=False)
