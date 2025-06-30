import pytest
from nfl_betting_app.nfl_pbp_analysis import (
    Game, Play, TeamSide, Touchdown, TouchdownType
)
# Import the private helper function for testing
from nfl_betting_app.feature_engineering import _get_all_stats_for_game

@pytest.fixture
def sample_game_for_fe() -> Game:
    """
    Provides a comprehensive Game object with plays covering various stats.
    Home: KC (1 pass TD, 1 rush TD, 15 rush yds, 20 pass yds, 1/1 3D, 0/1 4D)
    Away: SF (1 def TD, 20 rush yds, 30 pass yds, 0/1 3D, 1/1 4D)
    """
    plays = [
        # KC Plays
        Play(posteam='KC', down=1, rushing_yards=10, passing_yards=0),
        Play(posteam='KC', down=2, rushing_yards=5, passing_yards=0, touchdown=Touchdown(type=TouchdownType.RUSHING, scoring_team=TeamSide.HOME)),
        Play(posteam='KC', down=3, third_down_converted=True, third_down_failed=False, rushing_yards=0, passing_yards=20, touchdown=Touchdown(type=TouchdownType.PASSING, scoring_team=TeamSide.HOME)),
        Play(posteam='KC', down=4, fourth_down_converted=False, fourth_down_failed=True, rushing_yards=0, passing_yards=0),

        # SF Plays
        Play(posteam='SF', down=1, rushing_yards=20, passing_yards=0),
        Play(posteam='SF', down=2, rushing_yards=0, passing_yards=30),
        Play(posteam='SF', down=3, third_down_converted=False, third_down_failed=True, rushing_yards=0, passing_yards=0),
        Play(posteam='SF', down=4, fourth_down_converted=True, fourth_down_failed=False, rushing_yards=0, passing_yards=0),

        # Defensive TD for SF (posteam is KC)
        Play(posteam='KC', down=1, rushing_yards=0, passing_yards=0, touchdown=Touchdown(type=TouchdownType.DEFENCE, scoring_team=TeamSide.AWAY)),
    ]
    return Game(game_id='test_fe_game', home_team='KC', away_team='SF', plays=plays)


def test_get_all_stats_for_game(sample_game_for_fe: Game):
    """
    Tests the _get_all_stats_for_game helper to ensure it correctly aggregates stats.
    """
    all_stats = _get_all_stats_for_game(sample_game_for_fe)

    # --- Assert Structure ---
    expected_keys = [
        'passing_tds', 'rushing_tds', 'defence_tds', 'special_teams_tds',
        'rushing_yards', 'passing_yards', 'third_down_conv_rate', 'fourth_down_conv_rate'
    ]
    assert all(key in all_stats for key in expected_keys)
    assert all(TeamSide.HOME in v and TeamSide.AWAY in v for v in all_stats.values())

    # --- Assert Values ---
    # Touchdowns
    assert all_stats['passing_tds'][TeamSide.HOME] == 1
    assert all_stats['rushing_tds'][TeamSide.HOME] == 1
    assert all_stats['defence_tds'][TeamSide.AWAY] == 1
    assert all_stats['special_teams_tds'][TeamSide.HOME] == 0

    # Yards
    assert all_stats['rushing_yards'][TeamSide.HOME] == 15
    assert all_stats['passing_yards'][TeamSide.AWAY] == 30

    # Conversion Rates
    assert all_stats['third_down_conv_rate'][TeamSide.HOME] == 1.0
    assert all_stats['third_down_conv_rate'][TeamSide.AWAY] == 0.0
    assert all_stats['fourth_down_conv_rate'][TeamSide.HOME] == 0.0
    assert all_stats['fourth_down_conv_rate'][TeamSide.AWAY] == 1.0