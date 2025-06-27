import pandas as pd
import nfl_data_py as nfl
from datetime import date, timedelta
import os
import nfl_betting_app.config as config


def _get_latest_available_season() -> int:
    """
    Calculates the most recent NFL season for which data is likely available.
    """
    today = date.today()
    # If current date is before August 1st, the previous year is the latest completed season.
    # Otherwise, the current year's data (preseason/regular season) might be available.
    if today < date(today.year, 8, 1):
        return today.year - 1
    else:
        return today.year

def update_raw_pbp_data() -> None:
    """
    Maintains and updates the local RAW database of play-by-play data.
    """
    os.makedirs(config.RAW_DATA_DIR, exist_ok=True)
    latest_season = _get_latest_available_season()

    if os.path.exists(config.RAW_PBP_DB_PATH):
        df = pd.read_csv(config.RAW_PBP_DB_PATH, low_memory=False)
        last_year_in_db = int(df["season"].max())
        if last_year_in_db < latest_season:
            print(
                f"Raw PBP DB is outdated. Last season: {last_year_in_db}. Fetching new raw data..."
            )
            years_to_fetch = range(last_year_in_db + 1, latest_season + 1)

            if years_to_fetch:
                new_data = nfl.import_pbp_data(years=list(years_to_fetch))
                df = pd.concat([df, new_data], ignore_index=True)
                df.to_csv(config.RAW_PBP_DB_PATH, index=False)
    else:
        print(
            f"No local PBP DB found. Performing initial full load from {config.START_YEAR} to {latest_season}..."
        )
        years_to_fetch = range(config.START_YEAR, latest_season + 1)
        df = nfl.import_pbp_data(years=list(years_to_fetch))
        df.to_csv(config.RAW_PBP_DB_PATH, index=False)

    print(
        f"Raw PBP database is up to date. Location: {config.RAW_PBP_DB_PATH}"
    )

if __name__ == "__main__":
    print("--- Running All Raw Data Retrieval Functions ---")
    update_raw_pbp_data()
    print("\n--- All Raw Data Retrieval Complete ---")
