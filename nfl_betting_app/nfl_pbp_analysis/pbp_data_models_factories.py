import pandas as pd
from typing import Optional
from .pbp_data_models import Game, Play, Touchdown, TouchdownType, TeamSide

# These are the raw columns we need from the PBP data to construct our models.
REQUIRED_COLS = [
    'game_id', 'home_team', 'away_team', 'posteam', 'down',
    'third_down_converted', 'third_down_failed',
    'fourth_down_converted', 'fourth_down_failed',
    'rushing_yards', 'passing_yards',
    # Raw columns for building TouchdownInfo
    'pass_touchdown', 'rush_touchdown', 'return_touchdown',
    'interception', 'fumble_lost', 'td_team', 'td_player_name'
]

def _create_touchdown(row: pd.Series) -> Optional[Touchdown]:
    """
    Factory function to create a Touchdown object from a raw data row.
    Returns None if no touchdown occurred on the play.
    """
    td_type = None
    # nfl-py uses 0/1 for these boolean-like columns
    if row.get('pass_touchdown') == 1:
        td_type = TouchdownType.PASSING
    elif row.get('rush_touchdown') == 1:
        td_type = TouchdownType.RUSHING
    elif row.get('return_touchdown') == 1:
        # Defensive TDs are typically on interceptions or fumble returns
        if row.get('interception') == 1 or row.get('fumble_lost') == 1:
            td_type = TouchdownType.DEFENCE
        else:  # Otherwise, assume it's a special teams return (punt or kickoff)
            td_type = TouchdownType.SPECIAL_TEAMS

    if not td_type:
        return None

    scoring_team_abbr = row.get('td_team')
    if pd.isna(scoring_team_abbr):
        return None

    scoring_team_side = None
    if scoring_team_abbr == row.get('home_team'):
        scoring_team_side = TeamSide.HOME
    elif scoring_team_abbr == row.get('away_team'):
        scoring_team_side = TeamSide.AWAY

    if not scoring_team_side:
        return None

    return Touchdown(
        type=td_type,
        scoring_team=scoring_team_side,
        player_name=row.get('td_player_name')
    )

def game_from_single_game_dataframe(data_frame: pd.DataFrame)-> Game: 
    if not all(col in data_frame.columns for col in REQUIRED_COLS):
        missing = [col for col in REQUIRED_COLS if col not in data_frame.columns]
        raise ValueError(f"Missing required columns to form a Game: {missing}")
    if data_frame.empty:
        raise ValueError("Input DataFrame cannot be empty.")
    if data_frame['game_id'].nunique() > 1:
            raise ValueError("Input DataFrame contains data for more than one game.")
        
    play_objects = []
    for _, row in data_frame.iterrows():
        # Start with all the raw data from the row
        play_data = row.to_dict()
        
        # Explicitly handle fields that need transformation or validation
        # Convert potential NaN in 'down' to None for Pydantic
        if pd.isna(play_data.get('down')):
            play_data['down'] = None
            
        # Overwrite the raw 'touchdown' column (0.0/1.0) with the structured Touchdown object
        play_data['touchdown'] = _create_touchdown(row)
        
        play_objects.append(Play(**play_data))

    return Game(
        game_id=data_frame['game_id'].iloc[0],
        home_team=data_frame['home_team'].iloc[0],
        away_team=data_frame['away_team'].iloc[0],
        plays=play_objects
    )
