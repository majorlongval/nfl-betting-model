# nfl_betting_app/data_retriever.py
# This module is responsible for updating a LOCAL database of game data.
# It reads a local file, fetches new data from the web, and appends to it.

import pandas as pd
import nfl_data_py as nfl
from datetime import datetime
import os

# --- Configuration ---
# Define local storage locations
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LOCAL_GAMES_DB_PATH = os.path.join(DATA_DIR, "nfl_games_database.csv")


def update_local_game_data(start_year: int = 2006) -> pd.DataFrame:
    """
    Updates a local CSV database of NFL games.

    Workflow:
    1. Reads the local CSV database if it exists.
    2. Checks if new seasons need to be fetched from nfl_data_py.
    3. Appends new data to the local file.

    Args:
        start_year: The first season to fetch if no local database exists.

    Returns:
        A pandas DataFrame with the most up-to-date game data.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    current_season = datetime.now().year

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

    if os.path.exists(LOCAL_GAMES_DB_PATH):
        print(f"Loading local database from: {LOCAL_GAMES_DB_PATH}")
        df = pd.read_csv(LOCAL_GAMES_DB_PATH)
        last_year_in_db = int(df["season"].max())

        if last_year_in_db < current_season:
            print(
                f"Local database is outdated. Last season: {last_year_in_db}. Fetching new data from nfl_data_py..."
            )
            years_to_fetch = range(last_year_in_db + 1, current_season + 1)

            try:
                new_data = nfl.import_schedules(years=list(years_to_fetch))
                if not new_data.empty:
                    new_data_filtered = new_data.reindex(
                        columns=pertinent_columns
                    ).dropna()
                    df = pd.concat([df, new_data_filtered], ignore_index=True)
                    df.drop_duplicates(subset=["game_id"], keep="last", inplace=True)
                    df.to_csv(LOCAL_GAMES_DB_PATH, index=False)
                    print(
                        f"Local database updated with data for seasons: {list(years_to_fetch)}"
                    )
            except Exception as e:
                print(f"Could not fetch new data: {e}")
        else:
            print("Local database is already up to date.")

    else:
        # Local database does not exist, perform initial full load.
        print(
            f"No local database found. Performing initial full load from {start_year}..."
        )
        try:
            years_to_fetch = range(start_year, current_season + 1)
            df_full = nfl.import_schedules(years=list(years_to_fetch))
            df = df_full.reindex(columns=pertinent_columns).dropna()
            df.to_csv(LOCAL_GAMES_DB_PATH, index=False)
            print(f"Initial local database created at: {LOCAL_GAMES_DB_PATH}")
        except Exception as e:
            print(f"Failed to create initial database: {e}")
            return pd.DataFrame()

    return df


# This block allows you to run this specific script directly for testing
if __name__ == "__main__":
    print("--- Running Local Data Update Test ---")
    games_df = update_local_game_data()

    if games_df is not None and not games_df.empty:
        print("\n--- Local Update Successful ---")
        print(f"Total games in local database: {len(games_df)}")
        print(
            f"Seasons covered: {games_df['season'].min()} to {games_df['season'].max()}"
        )
