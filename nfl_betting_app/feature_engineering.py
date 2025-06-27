# nfl_betting_app/feature_engineering.py
# This module is responsible for processing the raw data and creating
# the final feature set for the model.

import pandas as pd
import os
import nfl_betting_app.config as config
from nfl_betting_app.data_handler import load_raw_game_data, load_raw_weekly_player_stats_data

# --- Constants for Feature Engineering ---
# Core player stats we can reliably aggregate to the team level
STATS_TO_AGGREGATE = [
    'passing_yards', 'rushing_yards', 'passing_tds', 'rushing_tds',
    'interceptions', 'rushing_fumbles_lost', 'receiving_fumbles_lost'
]
# The final team-level stats we will calculate averages for
STATS_TO_AVERAGE = ['yards_offense', 'tds_offense', 'giveaways', 
                    'yards_allowed', 'tds_allowed', 'takeaways', 'turnover_margin']
# The rolling window sizes (in games)
ROLLING_WINDOWS = [1, 3, 5]


def _aggregate_team_stats_from_weekly(weekly_stats_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates weekly player stats to the team level for both offense and defense.
    """
    print("  Step A: Aggregating player stats to team level...")
    
    # --- Offensive Stats ---
    # Group by the player's team to get offensive totals
    offense_df = weekly_stats_df.groupby(['season', 'week', 'recent_team'])[STATS_TO_AGGREGATE].sum().reset_index()
    offense_df.rename(columns={'recent_team': 'team'}, inplace=True)
    offense_df['yards_offense'] = offense_df['passing_yards'] + offense_df['rushing_yards']
    offense_df['tds_offense'] = offense_df['passing_tds'] + offense_df['rushing_tds']
    offense_df['giveaways'] = offense_df['interceptions'] + offense_df['rushing_fumbles_lost'] + offense_df['receiving_fumbles_lost']

    # --- Defensive Stats (Takeaways) ---
    # To get a team's takeaways, we sum the giveaways of their opponents
    defense_df = offense_df[['season', 'week', 'team', 'giveaways']].copy()
    defense_df.rename(columns={'giveaways': 'takeaways'}, inplace=True)

    # Merge offense with opponent's giveaways (which are the defense's takeaways)
    # First, get the opponent for each team each week from the games data
    games_teams = load_raw_game_data()[['season', 'week', 'home_team', 'away_team']]
    
    home_opponents = games_teams.rename(columns={'home_team': 'team', 'away_team': 'opponent'})
    away_opponents = games_teams.rename(columns={'away_team': 'team', 'home_team': 'opponent'})
    opponent_map = pd.concat([home_opponents, away_opponents]).drop_duplicates()

    # Merge opponent info onto our stats dataframe
    offense_df = pd.merge(offense_df, opponent_map, on=['season', 'week', 'team'], how='left')
    
    # Now merge the takeaways
    final_stats = pd.merge(offense_df, defense_df, left_on=['season', 'week', 'opponent'], right_on=['season', 'week', 'team'], how='left', suffixes=('', '_def'))
    final_stats.drop(columns=['team_def'], inplace=True)
    
    # A simple approximation for yards/tds allowed
    final_stats['yards_allowed'] = final_stats.groupby(['season', 'opponent'])['yards_offense'].shift(1)
    final_stats['tds_allowed'] = final_stats.groupby(['season', 'opponent'])['tds_offense'].shift(1)

    final_stats['turnover_margin'] = final_stats['takeaways'] - final_stats['giveaways']
    
    return final_stats.sort_values(by=['team', 'season', 'week'])

def _calculate_point_in_time_stats(team_stats_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates season-to-date (expanding) and rolling window averages for key stats.
    """
    print("  Step B: Calculating point-in-time rolling and expanding averages...")
    
    for col in STATS_TO_AVERAGE:
        expanding_avg = team_stats_df.groupby(['team', 'season'])[col].expanding().mean()
        team_stats_df[f'avg_{col}'] = expanding_avg.reset_index(level=[0,1], drop=True)
        
        for window in ROLLING_WINDOWS:
            rolling_avg = team_stats_df.groupby(['team', 'season'])[col].rolling(window=window, min_periods=1).mean()
            team_stats_df[f'l{window}_{col}'] = rolling_avg.reset_index(level=[0,1], drop=True)

    cols_to_shift = [f'avg_{col}' for col in STATS_TO_AVERAGE]
    for window in ROLLING_WINDOWS:
        cols_to_shift.extend([f'l{window}_{col}' for col in STATS_TO_AVERAGE])

    team_stats_df[cols_to_shift] = team_stats_df.groupby(['team', 'season'])[cols_to_shift].shift(1)
    team_stats_df.fillna(0, inplace=True)
    return team_stats_df

def _merge_features_to_games(games_df: pd.DataFrame, team_stats_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merges the calculated point-in-time stats onto the main games dataframe.
    """
    print("  Step C: Merging features with games data...")
    feature_cols = [f'avg_{col}' for col in STATS_TO_AVERAGE]
    for window in ROLLING_WINDOWS:
        feature_cols.extend([f'l{window}_{col}' for col in STATS_TO_AVERAGE])
        
    stats_for_merge = team_stats_df[['season', 'week', 'team'] + feature_cols]
    
    final_df = pd.merge(games_df, stats_for_merge, left_on=['season', 'week', 'home_team'], right_on=['season', 'week', 'team'], how='left')
    final_df.rename(columns={col: f'home_{col}' for col in feature_cols}, inplace=True)
    
    final_df = pd.merge(final_df, stats_for_merge, left_on=['season', 'week', 'away_team'], right_on=['season', 'week', 'team'], how='left')
    final_df.rename(columns={col: f'away_{col}' for col in feature_cols}, inplace=True)
    
    final_df.drop(columns=['team_x', 'team_y'], inplace=True, errors='ignore')
    return final_df


def create_final_feature_set(games_df: pd.DataFrame, weekly_stats_df: pd.DataFrame) -> pd.DataFrame:
    """
    Orchestrates the entire feature engineering pipeline for the MVP.
    """
    print("Starting MVP feature engineering pipeline...")
    
    # --- Step 1: Filter and Select Essential Columns ---
    # Filter for played games and select only the columns needed for modeling and simulation.
    essential_game_cols = [
        'game_id', 'season', 'week', 'home_team', 'away_team', 'spread_line', 'result'
    ]
    played_games_df = games_df.dropna(subset=['result'])[essential_game_cols].copy()
    print(f"Filtered down to {len(played_games_df)} played games.")
    
    team_weekly_stats = _aggregate_team_stats_from_weekly(weekly_stats_df)
    point_in_time_stats = _calculate_point_in_time_stats(team_weekly_stats)
    final_feature_df = _merge_features_to_games(played_games_df, point_in_time_stats)

    print("Feature engineering pipeline complete.")
    return final_feature_df


if __name__ == '__main__':
    print("--- Running Full MVP Feature Engineering Pipeline ---")
    
    try:
        raw_games_df = load_raw_game_data()
        raw_weekly_stats_df = load_raw_weekly_player_stats_data()

        if not raw_games_df.empty and not raw_weekly_stats_df.empty:
            feature_df = create_final_feature_set(raw_games_df, raw_weekly_stats_df)
            
            os.makedirs(config.PROCESSED_DATA_DIR, exist_ok=True)
            feature_df.to_csv(config.MODEL_FEATURE_SET_PATH, index=False)
            print(f"\nModel-ready feature set saved to: {config.MODEL_FEATURE_SET_PATH}")
            
            print("\n--- Example of Final Features ---")
            display_cols = ['game_id', 'home_team', 'away_team', 'home_avg_yards_offense', 'away_avg_yards_offense', 'home_l3_turnover_margin', 'away_l3_turnover_margin', 'spread_line']
            print(feature_df[display_cols].dropna().tail().to_string())

    except FileNotFoundError as e:
        print(f"\nERROR: A raw data file was not found. Details: {e}")
