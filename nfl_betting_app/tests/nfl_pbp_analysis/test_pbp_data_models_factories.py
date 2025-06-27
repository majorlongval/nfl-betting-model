import pandas as pd
import pytest

from nfl_betting_app.nfl_pbp_analysis.pbp_data_models import Game, Play
from nfl_betting_app.nfl_pbp_analysis.pbp_data_models_factories import (
    game_from_single_game_dataframe, REQUIRED_COLS
)


@pytest.fixture
def sample_game_df() -> pd.DataFrame:
    """Provides a sample DataFrame representing a single game."""
    data = {
        'game_id': ['2023_01_KC_SF'] * 3,
        'home_team': ['KC'] * 3,
        'away_team': ['SF'] * 3,
        'posteam': ['KC', 'KC', 'SF'],
        'down': [1, 2, 3],
        'third_down_converted': [False, False, True],
        'third_down_failed': [False, False, False],
        'extra_col': [10, 20, 30]  # To ensure extra columns are ignored
    }
    return pd.DataFrame(data)


def test_game_from_single_game_dataframe_success(sample_game_df: pd.DataFrame):
    """Tests successful creation of a Game object from a valid DataFrame."""
    game = game_from_single_game_dataframe(sample_game_df)

    assert isinstance(game, Game)
    assert game.game_id == '2023_01_KC_SF'
    assert game.home_team == 'KC'
    assert game.away_team == 'SF'
    assert len(game.plays) == 3

    # Check the first play
    assert isinstance(game.plays[0], Play)
    assert game.plays[0].posteam == 'KC'
    assert game.plays[0].down == 1
    assert not game.plays[0].third_down_converted
    assert not game.plays[0].third_down_failed

    # Check the last play
    assert game.plays[2].posteam == 'SF'
    assert game.plays[2].down == 3
    assert game.plays[2].third_down_converted
    assert not game.plays[2].third_down_failed


def test_game_from_dataframe_missing_columns(sample_game_df: pd.DataFrame):
    """Tests that a ValueError is raised if required columns are missing."""
    df_missing_col = sample_game_df.drop(columns=['down'])

    with pytest.raises(ValueError, match="Missing cols to form a Game"):
        game_from_single_game_dataframe(df_missing_col)


def test_game_from_dataframe_multiple_games():
    """Tests that a ValueError is raised if the DataFrame contains multiple games."""
    df_multiple_games_data = {
        'game_id': ['2023_01_KC_SF', '2023_01_BUF_MIA'],
        'home_team': ['KC', 'BUF'],
        'away_team': ['SF', 'MIA'],
        'posteam': ['KC', 'MIA'],
        'down': [1, 1],
        'third_down_converted': [False, False],
        'third_down_failed': [False, False],
    }
    df_multiple_games = pd.DataFrame(df_multiple_games_data)

    with pytest.raises(ValueError, match="Input DataFrame contains data for more than one game."):
        game_from_single_game_dataframe(df_multiple_games)


def test_game_from_dataframe_empty():
    """Tests that a ValueError is raised for an empty DataFrame."""
    empty_df = pd.DataFrame(columns=REQUIRED_COLS)

    with pytest.raises(ValueError, match="Input DataFrame cannot be empty."):
        game_from_single_game_dataframe(empty_df)