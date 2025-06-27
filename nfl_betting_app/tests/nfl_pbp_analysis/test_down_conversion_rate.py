import pytest
from typing import List
from nfl_betting_app.nfl_pbp_analysis.pbp_data_models import Game, Play, TeamSide
from nfl_betting_app.nfl_pbp_analysis.down_conversion_rate import (
    calculate_third_down_conversion_rate,
    calculate_fourth_down_conversion_rate
)

@pytest.fixture
def game_with_mixed_downs() -> Game:
    """
    Game with a mix of third and fourth down plays for both teams,
    including conversions and failures.
    """
    plays = [
        # KC 3rd downs (2 conv, 1 fail) -> 2/3
        Play(posteam='KC', down=3, third_down_converted=True, third_down_failed=False),
        Play(posteam='KC', down=3, third_down_converted=False, third_down_failed=True),
        Play(posteam='KC', down=3, third_down_converted=True, third_down_failed=False),

        # SF 3rd downs (1 conv, 1 fail) -> 1/2
        Play(posteam='SF', down=3, third_down_converted=False, third_down_failed=True),
        Play(posteam='SF', down=3, third_down_converted=True, third_down_failed=False),

        # KC 4th downs (1 conv, 1 fail) -> 1/2
        Play(posteam='KC', down=4, fourth_down_converted=True, fourth_down_failed=False),
        Play(posteam='KC', down=4, fourth_down_converted=False, fourth_down_failed=True),

        # SF 4th downs (2 conv, 1 fail) -> 2/3
        Play(posteam='SF', down=4, fourth_down_converted=True, fourth_down_failed=False),
        Play(posteam='SF', down=4, fourth_down_converted=True, fourth_down_failed=False),
        Play(posteam='SF', down=4, fourth_down_converted=False, fourth_down_failed=True),

        # Other downs
        Play(posteam='KC', down=1),
        Play(posteam='SF', down=2),
    ]
    return Game(game_id='game_mixed', home_team='KC', away_team='SF', plays=plays)

@pytest.fixture
def game_only_third_downs() -> Game:
    """Game with only third down plays."""
    plays = [
        Play(posteam='KC', down=3, third_down_converted=True, third_down_failed=False),
        Play(posteam='KC', down=3, third_down_converted=False, third_down_failed=True),
        Play(posteam='SF', down=3, third_down_converted=True, third_down_failed=False),
    ]
    return Game(game_id='game_only_3rd', home_team='KC', away_team='SF', plays=plays)

@pytest.fixture
def game_only_fourth_downs() -> Game:
    """Game with only fourth down plays."""
    plays = [
        Play(posteam='KC', down=4, fourth_down_converted=True, fourth_down_failed=False),
        Play(posteam='SF', down=4, fourth_down_converted=False, fourth_down_failed=True),
        Play(posteam='SF', down=4, fourth_down_converted=True, fourth_down_failed=False),
    ]
    return Game(game_id='game_only_4th', home_team='KC', away_team='SF', plays=plays)

@pytest.fixture
def game_no_conversion_attempts() -> Game:
    """Game with plays but no 3rd or 4th down attempts."""
    plays = [
        Play(posteam='KC', down=1),
        Play(posteam='SF', down=2),
        Play(posteam='KC', down=1),
    ]
    return Game(game_id='game_no_attempts', home_team='KC', away_team='SF', plays=plays)

@pytest.fixture
def empty_game() -> Game:
    """Game with no plays."""
    return Game(game_id='game_empty', home_team='KC', away_team='AWAY', plays=[])

@pytest.fixture
def game_third_down_home_no_attempts() -> Game:
    """Game for 3rd down test where home team has no attempts."""
    plays = [
        Play(posteam='SF', down=3, third_down_converted=True, third_down_failed=False),
        Play(posteam='SF', down=3, third_down_converted=False, third_down_failed=True),
    ]
    return Game(game_id='game_3rd_home_no', home_team='KC', away_team='SF', plays=plays)

@pytest.fixture
def game_third_down_away_no_attempts() -> Game:
    """Game for 3rd down test where away team has no attempts."""
    plays = [
        Play(posteam='KC', down=3, third_down_converted=True, third_down_failed=False),
        Play(posteam='KC', down=3, third_down_converted=False, third_down_failed=True),
    ]
    return Game(game_id='game_3rd_away_no', home_team='KC', away_team='SF', plays=plays)

@pytest.fixture
def game_fourth_down_home_no_attempts() -> Game:
    """Game for 4th down test where home team has no attempts."""
    plays = [
        Play(posteam='SF', down=4, fourth_down_converted=True, fourth_down_failed=False),
        Play(posteam='SF', down=4, fourth_down_converted=False, fourth_down_failed=True),
    ]
    return Game(game_id='game_4th_home_no', home_team='KC', away_team='SF', plays=plays)

@pytest.fixture
def game_fourth_down_away_no_attempts() -> Game:
    """Game for 4th down test where away team has no attempts."""
    plays = [
        Play(posteam='KC', down=4, fourth_down_converted=True, fourth_down_failed=False),
        Play(posteam='KC', down=4, fourth_down_converted=False, fourth_down_failed=True),
    ]
    return Game(game_id='game_4th_away_no', home_team='KC', away_team='SF', plays=plays)


# --- Tests for calculate_third_down_conversion_rate ---

def test_third_down_conversion_rate_standard(game_with_mixed_downs: Game):
    """Tests third down conversion rate with a mix of conversions and failures."""
    rates = calculate_third_down_conversion_rate(game_with_mixed_downs)
    # KC: 2 converted, 1 failed -> 2/3 = 0.666...
    # SF: 1 converted, 1 failed -> 1/2 = 0.5
    assert pytest.approx(rates[TeamSide.HOME]) == 2/3
    assert pytest.approx(rates[TeamSide.AWAY]) == 0.5

def test_third_down_conversion_rate_only_third_downs(game_only_third_downs: Game):
    """Tests third down conversion rate with only third down plays."""
    rates = calculate_third_down_conversion_rate(game_only_third_downs)
    # KC: 1 converted, 1 failed -> 1/2 = 0.5
    # SF: 1 converted, 0 failed -> 1/1 = 1.0
    assert pytest.approx(rates[TeamSide.HOME]) == 0.5
    assert pytest.approx(rates[TeamSide.AWAY]) == 1.0

def test_third_down_conversion_rate_home_no_attempts(game_third_down_home_no_attempts: Game):
    """Tests third down conversion rate when home team has no attempts."""
    rates = calculate_third_down_conversion_rate(game_third_down_home_no_attempts)
    assert rates[TeamSide.HOME] == 0.0
    assert pytest.approx(rates[TeamSide.AWAY]) == 0.5 # 1/2

def test_third_down_conversion_rate_away_no_attempts(game_third_down_away_no_attempts: Game):
    """Tests third down conversion rate when away team has no attempts."""
    rates = calculate_third_down_conversion_rate(game_third_down_away_no_attempts)
    assert pytest.approx(rates[TeamSide.HOME]) == 0.5 # 1/2
    assert rates[TeamSide.AWAY] == 0.0

def test_third_down_conversion_rate_no_attempts_at_all(game_no_conversion_attempts: Game):
    """Tests third down conversion rate when no 3rd down attempts occur."""
    rates = calculate_third_down_conversion_rate(game_no_conversion_attempts)
    assert rates[TeamSide.HOME] == 0.0
    assert rates[TeamSide.AWAY] == 0.0

def test_third_down_conversion_rate_empty_game(empty_game: Game):
    """Tests third down conversion rate with an empty game."""
    rates = calculate_third_down_conversion_rate(empty_game)
    assert rates[TeamSide.HOME] == 0.0
    assert rates[TeamSide.AWAY] == 0.0

# --- Tests for calculate_fourth_down_conversion_rate ---

def test_fourth_down_conversion_rate_standard(game_with_mixed_downs: Game):
    """Tests fourth down conversion rate with a mix of conversions and failures."""
    rates = calculate_fourth_down_conversion_rate(game_with_mixed_downs)
    # KC: 1 converted, 1 failed -> 1/2 = 0.5
    # SF: 2 converted, 1 failed -> 2/3 = 0.666...
    assert pytest.approx(rates[TeamSide.HOME]) == 0.5
    assert pytest.approx(rates[TeamSide.AWAY]) == 2/3

def test_fourth_down_conversion_rate_only_fourth_downs(game_only_fourth_downs: Game):
    """Tests fourth down conversion rate with only fourth down plays."""
    rates = calculate_fourth_down_conversion_rate(game_only_fourth_downs)
    # KC: 1 converted, 0 failed -> 1/1 = 1.0
    # SF: 1 converted, 1 failed -> 1/2 = 0.5
    assert pytest.approx(rates[TeamSide.HOME]) == 1.0
    assert pytest.approx(rates[TeamSide.AWAY]) == 0.5

def test_fourth_down_conversion_rate_home_no_attempts(game_fourth_down_home_no_attempts: Game):
    """Tests fourth down conversion rate when home team has no attempts."""
    rates = calculate_fourth_down_conversion_rate(game_fourth_down_home_no_attempts)
    assert rates[TeamSide.HOME] == 0.0
    assert pytest.approx(rates[TeamSide.AWAY]) == 0.5 # 1/2

def test_fourth_down_conversion_rate_away_no_attempts(game_fourth_down_away_no_attempts: Game):
    """Tests fourth down conversion rate when away team has no attempts."""
    rates = calculate_fourth_down_conversion_rate(game_fourth_down_away_no_attempts)
    assert pytest.approx(rates[TeamSide.HOME]) == 0.5 # 1/2
    assert rates[TeamSide.AWAY] == 0.0

def test_fourth_down_conversion_rate_no_attempts_at_all(game_no_conversion_attempts: Game):
    """Tests fourth down conversion rate when no 4th down attempts occur."""
    rates = calculate_fourth_down_conversion_rate(game_no_conversion_attempts)
    assert rates[TeamSide.HOME] == 0.0
    assert rates[TeamSide.AWAY] == 0.0

def test_fourth_down_conversion_rate_empty_game(empty_game: Game):
    """Tests fourth down conversion rate with an empty game."""
    rates = calculate_fourth_down_conversion_rate(empty_game)