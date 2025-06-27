import pytest
from nfl_betting_app.nfl_pbp_analysis.pbp_data_models import Game, Play, TeamSide, TouchdownType, Touchdown
from nfl_betting_app.nfl_pbp_analysis.score_analysis import (
    passing_touchdowns,
    rushing_touchdowns,
    defence_touchdowns,
    special_teams_touchdowns,
)

@pytest.fixture
def game_with_mixed_touchdowns() -> Game:
    """Game with a mix of touchdown types for both teams."""
    plays = [
        # KC (Home) Touchdowns - Offensive TDs
        Play(posteam='KC', down=1, touchdown=Touchdown(type=TouchdownType.PASSING, scoring_team=TeamSide.HOME)),
        Play(posteam='KC', down=2, touchdown=Touchdown(type=TouchdownType.PASSING, scoring_team=TeamSide.HOME)),
        Play(posteam='KC', down=3, touchdown=Touchdown(type=TouchdownType.RUSHING, scoring_team=TeamSide.HOME)),

        # SF (Away) Touchdowns - Mix of TD types
        Play(posteam='SF', down=1, touchdown=Touchdown(type=TouchdownType.RUSHING, scoring_team=TeamSide.AWAY)),
        Play(posteam='KC', down=2, touchdown=Touchdown(type=TouchdownType.DEFENCE, scoring_team=TeamSide.AWAY)),
        Play(posteam='KC', down=3, touchdown=Touchdown(type=TouchdownType.SPECIAL_TEAMS, scoring_team=TeamSide.AWAY)),

        # Plays without touchdowns
        Play(posteam='KC', down=1, touchdown=None),
        Play(posteam='SF', down=2, touchdown=None),
        Play(posteam='KC', down=1),
    ]
    return Game(game_id='mixed_td_game', home_team='KC', away_team='SF', plays=plays)

@pytest.fixture
def game_with_no_touchdowns() -> Game:
    """Game with plays but no touchdowns."""
    plays = [
        Play(posteam='KC', down=1, touchdown=None),
        Play(posteam='SF', down=1),
        Play(posteam='KC', down=2),
    ]
    return Game(game_id='no_td_game', home_team='KC', away_team='SF', plays=plays)

@pytest.fixture
def empty_game() -> Game:
    """Game with no plays."""
    return Game(game_id='empty_game', home_team='KC', away_team='SF', plays=[])

# --- Tests for passing_touchdowns ---
def test_passing_touchdowns_mixed(game_with_mixed_touchdowns: Game):
    tds = passing_touchdowns(game_with_mixed_touchdowns)
    assert tds[TeamSide.HOME] == 2
    assert tds[TeamSide.AWAY] == 0

def test_passing_touchdowns_none(game_with_no_touchdowns: Game):
    tds = passing_touchdowns(game_with_no_touchdowns)
    assert tds[TeamSide.HOME] == 0
    assert tds[TeamSide.AWAY] == 0

def test_passing_touchdowns_empty(empty_game: Game):
    tds = passing_touchdowns(empty_game)
    assert tds[TeamSide.HOME] == 0
    assert tds[TeamSide.AWAY] == 0

# --- Tests for rushing_touchdowns ---
def test_rushing_touchdowns_mixed(game_with_mixed_touchdowns: Game):
    tds = rushing_touchdowns(game_with_mixed_touchdowns)
    assert tds[TeamSide.HOME] == 1
    assert tds[TeamSide.AWAY] == 1

def test_rushing_touchdowns_none(game_with_no_touchdowns: Game):
    tds = rushing_touchdowns(game_with_no_touchdowns)
    assert tds[TeamSide.HOME] == 0
    assert tds[TeamSide.AWAY] == 0

# --- Tests for defence_touchdowns ---
def test_defence_touchdowns_mixed(game_with_mixed_touchdowns: Game):
    tds = defence_touchdowns(game_with_mixed_touchdowns)
    assert tds[TeamSide.HOME] == 0
    assert tds[TeamSide.AWAY] == 1

def test_defence_touchdowns_none(game_with_no_touchdowns: Game):
    tds = defence_touchdowns(game_with_no_touchdowns)
    assert tds[TeamSide.HOME] == 0
    assert tds[TeamSide.AWAY] == 0

# --- Tests for special_teams_touchdowns ---
def test_special_teams_touchdowns_mixed(game_with_mixed_touchdowns: Game):
    tds = special_teams_touchdowns(game_with_mixed_touchdowns)
    assert tds[TeamSide.HOME] == 0
    assert tds[TeamSide.AWAY] == 1

def test_special_teams_touchdowns_none(game_with_no_touchdowns: Game):
    tds = special_teams_touchdowns(game_with_no_touchdowns)
    assert tds[TeamSide.HOME] == 0
    assert tds[TeamSide.AWAY] == 0