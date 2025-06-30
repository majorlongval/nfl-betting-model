import pytest
from nfl_betting_app.nfl_pbp_analysis.pbp_data_models import Game, Play, TeamSide
from nfl_betting_app.nfl_pbp_analysis.game_statistics import (
    calculate_rushing_yards_per_game,
    calculate_passing_yards_per_game,
)

@pytest.fixture
def sample_game_stats() -> Game:
    """
    Provides a Game object with various plays to test different statistics.
    Home team: KC, Away team: SF
    """
    plays = [
        # KC Offensive Plays
        Play(posteam='KC', rushing_yards=10, passing_yards=0),
        Play(posteam='KC', rushing_yards=5, passing_yards=0),
        Play(posteam='KC', rushing_yards=0, passing_yards=25),
        Play(posteam='KC', rushing_yards=0, passing_yards=15),
        Play(posteam='KC', rushing_yards=-2, passing_yards=0), # Negative rush

        # SF Offensive Plays
        Play(posteam='SF', rushing_yards=8, passing_yards=0),
        Play(posteam='SF', rushing_yards=0, passing_yards=30),
        Play(posteam='SF', rushing_yards=0, passing_yards=10),
        Play(posteam='SF', rushing_yards=12, passing_yards=0),
        Play(posteam='SF', rushing_yards=0, passing_yards=-5), # Negative pass (sack)

        # Non-offensive plays or plays with no relevant stats
        Play(posteam='KC', down=1),
        Play(posteam='SF', down=2, rushing_yards=None, passing_yards=None),
    ]
    return Game(game_id='game_stats_test', home_team='KC', away_team='SF', plays=plays)

@pytest.fixture
def empty_game() -> Game:
    """Provides a Game object with no plays."""
    return Game(game_id='empty_game', home_team='HOME', away_team='AWAY', plays=[])

@pytest.fixture
def game_no_yards() -> Game:
    """Provides a Game object with plays but no yardage stats."""
    plays = [
        Play(posteam='KC', down=1, third_down_converted=True),
        Play(posteam='SF', down=2, fourth_down_failed=True),
    ]
    return Game(game_id='no_stats_game', home_team='KC', away_team='SF', plays=plays)


# --- Tests for calculate_rushing_yards_per_game ---
def test_calculate_rushing_yards_per_game(sample_game_stats: Game):
    yards = calculate_rushing_yards_per_game(sample_game_stats)
    # KC: 10 + 5 - 2 = 13
    # SF: 8 + 12 = 20
    assert yards[TeamSide.HOME] == 13.0
    assert yards[TeamSide.AWAY] == 20.0

def test_calculate_rushing_yards_empty_game(empty_game: Game):
    yards = calculate_rushing_yards_per_game(empty_game)
    assert yards[TeamSide.HOME] == 0.0
    assert yards[TeamSide.AWAY] == 0.0

def test_calculate_rushing_yards_no_relevant_stats(game_no_yards: Game):
    yards = calculate_rushing_yards_per_game(game_no_yards)
    assert yards[TeamSide.HOME] == 0.0
    assert yards[TeamSide.AWAY] == 0.0

# --- Tests for calculate_passing_yards_per_game ---
def test_calculate_passing_yards_per_game(sample_game_stats: Game):
    yards = calculate_passing_yards_per_game(sample_game_stats)
    # KC: 25 + 15 = 40
    # SF: 30 + 10 - 5 = 35
    assert yards[TeamSide.HOME] == 40.0
    assert yards[TeamSide.AWAY] == 35.0