# nfl_betting_app/feature_engineering.py
# This module is responsible for processing the raw data and creating
# the final feature set for the model.
from typing import Dict, Union
import pandas as pd
from tqdm import tqdm

# Import the analysis library components
from nfl_betting_app.nfl_pbp_analysis import (
    game_from_single_game_dataframe,
    passing_touchdowns,
    rushing_touchdowns,
    defence_touchdowns,
    special_teams_touchdowns,
    calculate_rushing_yards_per_game,
    calculate_passing_yards_per_game,
    third_down_conversion_rate,
    fourth_down_conversion_rate,
    TeamSide, Game,
    passing_touchdowns_allowed,
    rushing_touchdowns_allowed,
    calculate_rushing_yards_allowed_per_game,
    calculate_passing_yards_allowed_per_game,
    third_down_conversion_rate_allowed,
    fourth_down_conversion_rate_allowed
)

STATS_TO_CALCULATE = [
    # Offensive Stats
    'passing_tds', 'rushing_tds', 'defence_tds', 'special_teams_tds',
    'rushing_yards', 'passing_yards',
    'third_down_conv_rate', 'fourth_down_conv_rate',
    # Defensive Stats
    'passing_tds_allowed', 'rushing_tds_allowed',
    'rushing_yards_allowed', 'passing_yards_allowed',
    'third_down_conv_rate_allowed', 'fourth_down_conv_rate_allowed'
]
# The rolling window sizes (in games)
ROLLING_WINDOWS = [1, 3]


def _get_all_stats_for_game(game: Game) -> Dict[str, Dict[TeamSide, Union[float, int]]]:
    """
    Runs all analysis functions for a single Game object and returns a structured dictionary.
    This encapsulates all the calls to the analysis library.
    """
    return {
        # Offensive Stats
        'passing_tds': passing_touchdowns(game),
        'rushing_tds': rushing_touchdowns(game),
        'defence_tds': defence_touchdowns(game),
        'special_teams_tds': special_teams_touchdowns(game),
        'rushing_yards': calculate_rushing_yards_per_game(game),
        'passing_yards': calculate_passing_yards_per_game(game),
        'third_down_conv_rate': third_down_conversion_rate(game),
        'fourth_down_conv_rate': fourth_down_conversion_rate(game),
        # Defensive Stats (Allowed by this team's defense)
        'passing_tds_allowed': passing_touchdowns_allowed(game),
        'rushing_tds_allowed': rushing_touchdowns_allowed(game),
        'rushing_yards_allowed': calculate_rushing_yards_allowed_per_game(game),
        'passing_yards_allowed': calculate_passing_yards_allowed_per_game(game),
        'third_down_conv_rate_allowed': third_down_conversion_rate_allowed(game),
        'fourth_down_conv_rate_allowed': fourth_down_conversion_rate_allowed(game),
    }

def _calculate_team_game_stats(pbp_df: pd.DataFrame, season_type: str) -> pd.DataFrame:
    """
    Calculates team-level stats for each game from the PBP data for a specific season type.
    The output is a DataFrame with one row per team, per game.
    """
    # Filter for the specified season type and drop plays with no posteam.
    pbp_df_filtered = pbp_df[
        (pbp_df['season_type'] == season_type) & (pbp_df['posteam'].notna())
    ].copy()

    print(f"  Step A: Calculating team-level stats for {pbp_df_filtered['game_id'].nunique()} {season_type} games...")

    game_stats = []

    # Group by game_id and iterate
    for game_id, game_df in tqdm(pbp_df_filtered.groupby('game_id'), desc=f"Processing {season_type} Games"):
        game = game_from_single_game_dataframe(game_df)
        all_stats = _get_all_stats_for_game(game)

        # Structure the results for home and away teams
        home_stats = {
            'team': game.home_team, 'opponent': game.away_team,
            **{stat_name: stats[TeamSide.HOME] for stat_name, stats in all_stats.items()}
        }

        away_stats = {
            'team': game.away_team, 'opponent': game.home_team,
            **{stat_name: stats[TeamSide.AWAY] for stat_name, stats in all_stats.items()}
        }

        # Add game identifiers to each record
        for stats in [home_stats, away_stats]:
            stats['game_id'] = game_id
            stats['season'] = game_df['season'].iloc[0]
            stats['week'] = game_df['week'].iloc[0]

        game_stats.extend([home_stats, away_stats])

    return pd.DataFrame(game_stats)

def _calculate_rolling_averages(team_game_stats_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates point-in-time rolling and expanding averages for all stats.

    This function takes the team-game-level stats and computes rolling and
    expanding averages, shifting the results to prevent data leakage.
    """
    print("  Step B: Calculating point-in-time rolling averages...")

    # Sort values to ensure chronological order for rolling calculations
    df = team_game_stats_df.sort_values(by=['team', 'season', 'week']).copy()

    # --- Calculate Rolling and Expanding Averages ---
    feature_cols = []
    for col in tqdm(STATS_TO_CALCULATE, desc="Calculating Averages"):
        # Calculate expanding average (season-to-date)
        expanding_avg_col = f'avg_{col}'
        expanding_avg = df.groupby(['team', 'season'])[col].expanding().mean()
        df[expanding_avg_col] = expanding_avg.reset_index(level=[0, 1], drop=True)
        feature_cols.append(expanding_avg_col)

        # Calculate rolling window averages
        for window in ROLLING_WINDOWS:
            rolling_avg_col = f'l{window}_{col}'
            rolling_avg = df.groupby(['team', 'season'])[col].rolling(window=window, min_periods=1).mean()
            df[rolling_avg_col] = rolling_avg.reset_index(level=[0, 1], drop=True)
            feature_cols.append(rolling_avg_col)

    # Shift all calculated features to prevent data leakage from the current game
    df[feature_cols] = df.groupby(['team', 'season'])[feature_cols].shift(1)

    # Fill NaNs created by the shift (e.g., for the first game of a season) with 0
    df.fillna(0, inplace=True)

    return df

def _merge_features_to_games(pbp_df: pd.DataFrame, point_in_time_stats_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merges the point-in-time team stats back to a game-level DataFrame.
    """
    print("  Step C: Merging point-in-time stats to game-level data...")

    # First, create a clean, unique-per-game DataFrame from the PBP data
    game_level_df = pbp_df[[
        'game_id', 'season', 'week', 'home_team', 'away_team', 'spread_line', 'total_line', 'result'
    ]].drop_duplicates(subset=['game_id']).reset_index(drop=True)

    # Filter for played games only
    game_level_df = game_level_df.dropna(subset=['result']).copy()

    # Select only the feature columns we calculated
    feature_cols = [col for col in point_in_time_stats_df.columns if col.startswith(('avg_', 'l'))]
    stats_for_merge = point_in_time_stats_df[['game_id', 'team'] + feature_cols]

    # Merge for the home team
    final_df = pd.merge(
        game_level_df,
        stats_for_merge,
        left_on=['game_id', 'home_team'],
        right_on=['game_id', 'team'],
        how='left'
    ).rename(columns={col: f'home_{col}' for col in feature_cols})

    # Merge for the away team
    final_df = pd.merge(
        final_df,
        stats_for_merge,
        left_on=['game_id', 'away_team'],
        right_on=['game_id', 'team'],
        how='left',
        suffixes=('_home_merge', '_away_merge')
    ).rename(columns={col: f'away_{col}' for col in feature_cols})

    # Clean up intermediate columns from the merges
    final_df.drop(columns=['team_home_merge', 'team_away_merge'], inplace=True, errors='ignore')

    return final_df

def create_final_feature_set(pbp_df: pd.DataFrame, season_type: str = 'REG') -> pd.DataFrame:
    """
    Orchestrates the entire feature engineering pipeline using play-by-play data.

    Args:
        pbp_df: The raw play-by-play DataFrame.
        season_type: The type of season to process ('REG' or 'POST').
    """
    print(f"Starting PBP feature engineering pipeline for season_type='{season_type}'...")

    # Step 1: Calculate per-game stats using the analysis library.
    team_game_stats_df = _calculate_team_game_stats(pbp_df, season_type=season_type)

    # Step 2: Calculate rolling and expanding averages for these stats.
    point_in_time_stats_df = _calculate_rolling_averages(team_game_stats_df)

    # Step 3: Merge features back to a game-level DataFrame.
    final_feature_df = _merge_features_to_games(pbp_df, point_in_time_stats_df)

    # Step 4: Filter out Week 1 games, as they have no historical data
    final_feature_df = final_feature_df[final_feature_df['week'] > 1].copy()

    print("Feature engineering pipeline complete.")
    return final_feature_df
