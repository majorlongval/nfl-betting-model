import pandas as pd
import nfl_data_py as nfl
from datetime import datetime, date, timedelta
import os
import calendar
import nfl_betting_app.config as config


def _get_latest_available_season() -> int:
    """
    Calculates the most recent NFL season for which data is likely available.
    """
    today = date.today()
    first_day_of_sept = date(today.year, 9, 1)
    days_to_monday = (0 - first_day_of_sept.weekday() + 7) % 7
    first_monday = first_day_of_sept + timedelta(days=days_to_monday)
    season_start_date = first_monday + timedelta(days=3)

    if today < season_start_date:
        return today.year - 1
    else:
        return today.year


def update_raw_game_data() -> None:
    """
    Maintains and updates the local RAW database of NFL games and odds.
    """
    os.makedirs(config.RAW_DATA_DIR, exist_ok=True)
    latest_season = _get_latest_available_season()

    if os.path.exists(config.RAW_GAMES_DB_PATH):
        df = pd.read_csv(config.RAW_GAMES_DB_PATH, low_memory=False)
        last_year_in_db = int(df["season"].max())
        if last_year_in_db < latest_season:
            print(
                f"Raw Games DB is outdated. Last season: {last_year_in_db}. Fetching new raw data..."
            )
            years_to_fetch = range(last_year_in_db + 1, latest_season + 1)

            # --- ADDED DEFENSIVE CHECK ---
            if years_to_fetch:
                new_data = nfl.import_schedules(years=list(years_to_fetch))
                df = pd.concat([df, new_data], ignore_index=True)
                df.to_csv(config.RAW_GAMES_DB_PATH, index=False)
    else:
        print(
            f"No local raw games DB found. Performing initial full load from {config.START_YEAR} to {latest_season}..."
        )
        years_to_fetch = range(config.START_YEAR, latest_season + 1)
        df = nfl.import_schedules(years=list(years_to_fetch))
        df.to_csv(config.RAW_GAMES_DB_PATH, index=False)

    print(f"Raw games database is up to date. Location: {config.RAW_GAMES_DB_PATH}")


def update_raw_weekly_stats_data() -> None:
    """
    Maintains and updates the local RAW database of weekly player stats.
    """
    os.makedirs(config.RAW_DATA_DIR, exist_ok=True)
    latest_season = _get_latest_available_season()

    if os.path.exists(config.RAW_STATS_DB_PATH):
        df = pd.read_csv(config.RAW_STATS_DB_PATH, low_memory=False)
        last_year_in_db = int(df["season"].max())
        if last_year_in_db < latest_season:
            print(
                f"Raw Weekly Stats DB is outdated. Last season: {last_year_in_db}. Fetching new raw data..."
            )
            years_to_fetch = range(last_year_in_db + 1, latest_season + 1)

            # --- ADDED DEFENSIVE CHECK ---
            if years_to_fetch:
                new_data = nfl.import_weekly_data(years=list(years_to_fetch))
                df = pd.concat([df, new_data], ignore_index=True)
                df.to_csv(config.RAW_STATS_DB_PATH, index=False)
    else:
        print(
            f"No local weekly stats DB found. Performing initial full load from {config.START_YEAR} to {latest_season}..."
        )
        years_to_fetch = range(config.START_YEAR, latest_season + 1)
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

