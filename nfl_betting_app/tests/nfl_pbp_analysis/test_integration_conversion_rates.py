import pandas as pd
import pytest

from nfl_betting_app.nfl_pbp_analysis.pbp_data_models import TeamSide
from nfl_betting_app.nfl_pbp_analysis.pbp_data_models_factories import game_from_single_game_dataframe
from nfl_betting_app.nfl_pbp_analysis.down_conversion_rate import (
    calculate_third_down_conversion_rate,
    calculate_fourth_down_conversion_rate
)

@pytest.fixture
def sample_nfl_py_dataframe() -> pd.DataFrame:
    """
    Mocks a pandas DataFrame that would come from an nfl-py play-by-play export
    for a single game, including relevant columns for down conversion.
    """
    data = {
        'game_id': ['2023_01_BAL_CIN'] * 9,
        'home_team': ['CIN'] * 9,
        'away_team': ['BAL'] * 9,
        'posteam': ['BAL', 'CIN', 'BAL', 'CIN', 'BAL', 'CIN', 'BAL', 'CIN', 'BAL'],
        'down': [3, 3, 3, 3, 4, 4, 4, 4, 1],
        'third_down_converted': [True, False, False, True, False, False, False, False, False],
        'third_down_failed': [False, True, True, False, False, False, False, False, False],
        'fourth_down_converted': [False, False, False, False, True, False, False, True, False],
        'fourth_down_failed': [False, False, False, False, False, True, True, False, False],
        # Include other common nfl-py columns to make it more realistic,
        # even if not directly used by our factory for Play objects
        'play_id': range(1, 10),
        'desc': ['Play 1', 'Play 2', 'Play 3', 'Play 4', 'Play 5', 'Play 6', 'Play 7', 'Play 8', 'Play 9'],
        'qtr': [1]*9,
        'yrdln': [50]*9,
        'yards_gained': [5, -2, 10, 7, 3, -1, 0, 5, 8]
    }
    return pd.DataFrame(data)

def test_full_conversion_rate_pipeline(sample_nfl_py_dataframe: pd.DataFrame):
    """
    Tests the full pipeline: DataFrame -> Game Model -> Conversion Rate Calculation.
    """
    # Step 1: Create Game object from DataFrame using the factory
    game = game_from_single_game_dataframe(sample_nfl_py_dataframe)

    # Assert basic game properties
    assert game.game_id == '2023_01_BAL_CIN'
    assert game.home_team == 'CIN'
    assert game.away_team == 'BAL'
    assert len(game.plays) == 9

    # Step 2: Calculate Third Down Conversion Rates
    third_down_rates = calculate_third_down_conversion_rate(game)

    # Expected values:
    # BAL (Away): 1 converted (Play 1), 1 failed (Play 3) -> 1/2 = 0.5
    # CIN (Home): 1 converted (Play 4), 1 failed (Play 2) -> 1/2 = 0.5
    assert pytest.approx(third_down_rates[TeamSide.AWAY]) == 0.5
    assert pytest.approx(third_down_rates[TeamSide.HOME]) == 0.5

    # Step 3: Calculate Fourth Down Conversion Rates
    fourth_down_rates = calculate_fourth_down_conversion_rate(game)

    # Expected values:
    # BAL (Away): 1 converted (Play 5), 1 failed (Play 7) -> 1/2 = 0.5
    # CIN (Home): 1 converted (Play 8), 1 failed (Play 6) -> 1/2 = 0.5
    assert pytest.approx(fourth_down_rates[TeamSide.AWAY]) == 0.5
    assert pytest.approx(fourth_down_rates[TeamSide.HOME]) == 0.5

    # Verify that the keys are indeed TeamSide enums
    assert TeamSide.HOME in third_down_rates
    assert TeamSide.AWAY in third_down_rates
    assert TeamSide.HOME in fourth_down_rates
    assert TeamSide.AWAY in fourth_down_rates

    # Verify that no other keys are present
    assert len(third_down_rates) == 2
    assert len(fourth_down_rates) == 2