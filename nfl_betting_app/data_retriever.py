# nfl_betting_app/data_retriever.py
# This module is responsible for fetching raw data from external sources.

import pandas as pd
import nfl_data_py as nfl
from datetime import datetime
import os

# Define the path for our local data storage.
# The 'data' directory should be in the root of the project, one level above this script.
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
GAMES_DB_PATH = os.path.join(DATA_DIR, "nfl_games_database.csv")


def get_game_data(start_year: int = 2006) -> pd.DataFrame:
    """
    Maintains and loads a local CSV database of NFL game data.

    On first run, it creates the database. On subsequent runs, it checks for the
    latest data and appends only the missing seasons. It ensures no rows with
    missing data in pertinent columns are saved.

    Args:
        start_year: The first season to fetch. Defaults to 2006, when reliable
                    odds data becomes available.

    Returns:
        A pandas DataFrame with the filtered game-level data.
    """
    # Ensure the data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    # Determine the current NFL season. The season year is the year it starts.
    current_season = datetime.now().year
    df = None

    # Define the specific columns we want to keep for our project
    pertinent_columns = [
        "game_id",
        "season",
        "game_type",
        "week",
        "gameday",
        "away_team",
        "away_score",
        "home_team",
        "home_score",
        "result",
        "total",
        "away_moneyline",
        "home_moneyline",
        "spread_line",
        "away_spread_odds",
        "home_spread_odds",
        "total_line",
        "under_odds",
        "over_odds",
    ]

    if os.path.exists(GAMES_DB_PATH):
        print(f"Loading existing game database from: {GAMES_DB_PATH}")
        df = pd.read_csv(GAMES_DB_PATH)
        # Use int() to ensure we are comparing numbers, not strings or floats
        last_year_in_db = int(df["season"].max())

        if last_year_in_db < current_season:
            print(
                f"Database is outdated. Last season: {last_year_in_db}. Fetching new data..."
            )
            years_to_fetch = range(last_year_in_db + 1, current_season + 1)

            try:
                new_data = nfl.import_schedules(years=list(years_to_fetch))
                if not new_data.empty:
                    # Filter for only the columns we need
                    new_data_filtered = new_data.reindex(columns=pertinent_columns)

                    # --- ADDED CHECK ---
                    # Drop rows that have any missing data in our selected columns
                    new_data_filtered.dropna(inplace=True)

                    df = pd.concat([df, new_data_filtered], ignore_index=True)
                    # The 'game_id' is unique and reliable for deduplication
                    df.drop_duplicates(subset=["game_id"], keep="last", inplace=True)
                    df.to_csv(GAMES_DB_PATH, index=False)
                    print(
                        f"Database updated with data for seasons: {list(years_to_fetch)}"
                    )
                else:
                    print("No new season data found to append.")
            except Exception as e:
                print(f"Could not fetch new data: {e}")
        else:
            print("Game database is up to date.")

    else:
        # Database file does not exist, perform initial full load.
        print(
            f"No local database found. Performing initial full load from {start_year}..."
        )
        try:
            years_to_fetch = range(start_year, current_season + 1)
            df_full = nfl.import_schedules(years=list(years_to_fetch))

            # Filter the initial DataFrame to keep only the selected columns
            df_filtered = df_full.reindex(columns=pertinent_columns)

            # --- ADDED CHECK ---
            # Drop rows that have any missing data in our selected columns
            df = df_filtered.dropna()

            df.to_csv(GAMES_DB_PATH, index=False)
            print(f"Initial database created and saved to {GAMES_DB_PATH}")
        except Exception as e:
            print(f"Failed to create initial database: {e}")
            return pd.DataFrame()

    return df


# This block allows you to run the script directly to test it
if __name__ == "__main__":
    print("Running data retrieval test...")

    games_df = get_game_data()

    if not games_df.empty:
        print("\nData retrieval successful.")
        print(f"Total games in database: {len(games_df)}")
        print(
            f"Seasons covered: {games_df['season'].min()} to {games_df['season'].max()}"
        )
        print(
            f"Columns in database ({len(games_df.columns)}): {list(games_df.columns)}"
        )
        print("\nLast 5 entries:")
        print(games_df.tail())
        print(games_df["away_moneyline"])
