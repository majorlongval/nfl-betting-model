import pandas as pd
import os
import nfl_betting_app.config as config
from nfl_betting_app.data_handler import (
    load_raw_game_data,
    load_raw_weekly_player_stats_data,
)


def create_point_in_time_features(
    games_df: pd.DataFrame, weekly_stats_df: pd.DataFrame
) -> pd.DataFrame:
    print("Starting feature engineering process")

    played_games_df = games_df.dropna(subset=["result"]).copy()
    print(f"Filtered down to {len(played_games_df)} played games")

    stats_to_aggregate = [
        "passing_yards",
        "rushing_yards",
        "passing_tds",
        "rushing_tds",
        "interceptions",
        "sacks",
        "rushing_fumbles_lost",
        "receiving_fumbles_lost",
        "passing_epa",
        "rushing_epa",
        "attempts",
        "carries",
    ]
    team_weekly_stats = (
        weekly_stats_df.groupby(["season", "week", "recent_team"])[stats_to_aggregate]
        .sum()
        .reset_index()
    )

    team_weekly_stats["yards_offense"] = (
        team_weekly_stats["passing_yards"] + team_weekly_stats["rushing_yards"]
    )
    team_weekly_stats["tds_offense"] = (
        team_weekly_stats["passing_tds"] + team_weekly_stats["rushing_tds"]
    )
    team_weekly_stats["giveaways"] = (
        team_weekly_stats["interceptions"]
        + team_weekly_stats["rushing_fumbles_lost"]
        + team_weekly_stats["receiving_fumbles_lost"]
    )
    team_weekly_stats["total_epa"] = (
        team_weekly_stats["passing_epa"] + team_weekly_stats["rushing_epa"]
    )

    team_weekly_stats.sort_values(by=["recent_team", "season", "week"], inplace=True)

    cols_to_average = ["yards_offense", "tds_offense", "giveaways", "total_epa"]
    for col in cols_to_average:
        expanding_avg = (
            team_weekly_stats.groupby(["recent_team", "season"])[col].expanding().mean()
        )
        team_weekly_stats[f"avg_{col}"] = expanding_avg.reset_index(
            level=[0, 1], drop=True
        )

        # --- Step 5: Prevent Data Leakage ---
    # Shift the data so that week 5 contains the average from weeks 1-4.
    cols_to_shift = [f"avg_{col}" for col in cols_to_average]
    team_weekly_stats[cols_to_shift] = team_weekly_stats.groupby([
        "recent_team",
        "season",
    ])[cols_to_shift].shift(1)

    # --- Step 6: Merge features onto the main games DataFrame ---
    print("Merging features with games data...")
    stats_for_merge = team_weekly_stats.rename(columns={"recent_team": "team"})

    # Merge for the HOME team
    final_df = pd.merge(
        played_games_df,
        stats_for_merge,
        left_on=["season", "week", "home_team"],
        right_on=["season", "week", "team"],
        how="left",
    )
    final_df.rename(columns={col: f"home_{col}" for col in cols_to_shift}, inplace=True)

    # Merge for the AWAY team
    final_df = pd.merge(
        final_df,
        stats_for_merge,
        left_on=["season", "week", "away_team"],
        right_on=["season", "week", "team"],
        how="left",
        suffixes=("", "_away"),
    )
    final_df.rename(columns={col: f"away_{col}" for col in cols_to_shift}, inplace=True)

    # Clean up merged columns
    if "team" in final_df.columns:
        final_df.drop(columns=["team"], inplace=True)
    if "team_away" in final_df.columns:
        final_df.drop(columns=["team_away"], inplace=True)

    print("Feature engineering complete.")
    return final_df


if __name__ == "__main__":
    print("--- Running Feature Engineering Pipeline ---")

    try:
        # 1. Load the raw data using our handler
        games_df = load_raw_game_data()
        weekly_stats_df = load_raw_weekly_player_stats_data()

        if not games_df.empty and not weekly_stats_df.empty:
            # 2. Generate the final feature set
            feature_df = create_point_in_time_features(games_df, weekly_stats_df)

            # 3. Save the processed data to the 'processed' directory
            os.makedirs(config.PROCESSED_DATA_DIR, exist_ok=True)
            feature_df.to_csv(config.MODEL_FEATURE_SET_PATH, index=False)
            print(
                f"\nModel-ready feature set saved to: {config.MODEL_FEATURE_SET_PATH}"
            )

            print("\n--- Example of Final Features (last 5 games) ---")
            # Display relevant columns to check our work
            display_cols = [
                "game_id",
                "home_team",
                "away_team",
                "home_avg_yards_offense",
                "away_avg_yards_offense",
                "home_avg_total_epa",
                "away_avg_total_epa",
                "spread_line",
            ]
            print(feature_df[display_cols].dropna().tail().to_string())

    except FileNotFoundError as e:
        print(f"\nERROR: A raw data file was not found.")
        print(f"Details: {e}")
        print(
            "Please run the data_retriever.py script first to create the raw data files."
        )
