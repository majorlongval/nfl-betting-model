import pandas as pd
import nfl_data_py as nfl
from datetime import datetime
import os
import nfl_betting_app.config as config


def update_raw_game_data() -> None:
    """
    Maintains and updates the local RAW database of NFL games and odds.
    Saves the full, unfiltered data.
    """
    os.makedirs(config.RAW_DATA_DIR, exist_ok=True)
    current_season = datetime.now().year

    if os.path.exists(config.RAW_GAMES_DB_PATH):
        df = pd.read_csv(config.RAW_GAMES_DB_PATH, low_memory=False)
        last_year_in_db = int(df["season"].max())
        if last_year_in_db < current_season:
            print(
                f"Raw Games DB is outdated. Last season: {last_year_in_db}. Fetching new raw data..."
            )
            years_to_fetch = range(last_year_in_db + 1, current_season + 1)
            new_data = nfl.import_schedules(years=list(years_to_fetch))
            # Append the full raw data
            df = pd.concat([df, new_data], ignore_index=True)
            df.to_csv(config.RAW_GAMES_DB_PATH, index=False)
    else:
        print(
            f"No local raw games DB found. Performing initial full load from {config.START_YEAR}..."
        )
        years_to_fetch = range(config.START_YEAR, current_season + 1)
        df = nfl.import_schedules(years=list(years_to_fetch))
        df.to_csv(config.RAW_GAMES_DB_PATH, index=False)

    print(f"Raw games database is up to date. Location: {config.RAW_GAMES_DB_PATH}")


def update_raw_weekly_stats_data() -> None:
    """
    Maintains and updates the local RAW database of weekly player stats.
    """
    os.makedirs(config.RAW_DATA_DIR, exist_ok=True)
    current_season = datetime.now().year

    if os.path.exists(config.RAW_STATS_DB_PATH):
        df = pd.read_csv(config.RAW_STATS_DB_PATH, low_memory=False)
        last_year_in_db = int(df["season"].max())
        if last_year_in_db < current_season:
            print(
                f"Raw Weekly Stats DB is outdated. Last season: {last_year_in_db}. Fetching new raw data..."
            )
            years_to_fetch = range(last_year_in_db + 1, current_season)
            new_data = nfl.import_weekly_data(years=list(years_to_fetch))
            df = pd.concat([df, new_data], ignore_index=True)
            df.to_csv(config.RAW_STATS_DB_PATH, index=False)
    else:
        print(
            f"No local weekly stats DB found. Performing initial full load from {config.START_YEAR}..."
        )
        years_to_fetch = range(config.START_YEAR, current_season)
        df = nfl.import_weekly_data(years=list(years_to_fetch))
        df.to_csv(config.RAW_STATS_DB_PATH, index=False)

    print(
        f"Raw weekly stats database is up to date. Location: {config.RAW_STATS_DB_PATH}"
    )


if __name__ == "__main__":
    print("--- Running All Raw Data Retrieval Functions ---")
    update_raw_game_data()
    update_raw_weekly_stats_data()
    print("\n--- All Raw Data Retrieval Complete ---")
