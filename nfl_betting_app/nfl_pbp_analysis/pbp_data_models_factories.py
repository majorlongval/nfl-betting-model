import pandas as pd
from .pbp_data_models import Game, Play

REQUIRED_COLS = ['game_id', 'home_team', 'away_team', 'posteam', 'down',
                         'third_down_converted', 'third_down_failed',
                         'fourth_down_converted', 'fourth_down_failed']

def game_from_single_game_dataframe(data_frame: pd.DataFrame)-> Game: 
    if not all(col in data_frame.columns for col in REQUIRED_COLS):
        raise ValueError("Missing cols to form a Game")
    if data_frame.empty:
        raise ValueError("Input DataFrame cannot be empty.")
    if data_frame['game_id'].nunique() > 1:
            raise ValueError("Input DataFrame contains data for more than one game.")
        
    play_records = data_frame[REQUIRED_COLS].to_dict('records')
    
    play_objects = [Play(**record) for record in play_records]

    return Game(
        game_id=data_frame['game_id'].iloc[0],
        home_team=data_frame['home_team'].iloc[0],
        away_team=data_frame['away_team'].iloc[0],
        plays=play_objects
    )
