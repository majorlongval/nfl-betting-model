import pytest
from typing import List

from nfl_betting_app.nfl_pbp_analysis.pbp_data_models import Play, Game


@pytest.fixture
def sample_plays() -> List[Play]:
    """Provides a sample list of Play objects for testing."""
    return [
        Play(posteam='KC', down=1, third_down_converted=False, third_down_failed=False),
        Play(posteam='KC', down=2, third_down_converted=False, third_down_failed=False),
        Play(posteam='KC', down=3, third_down_converted=True, third_down_failed=False),
        Play(posteam='SF', down=1, third_down_converted=False, third_down_failed=False),
        Play(posteam='SF', down=2, third_down_converted=False, third_down_failed=False),
        Play(posteam='SF', down=3, third_down_converted=False, third_down_failed=True),
    ]


@pytest.fixture
def sample_game(sample_plays: List[Play]) -> Game:
    """Provides a sample Game object populated with plays."""
    return Game(
        game_id='2023_01_KC_SF',
        home_team='KC',
        away_team='SF',
        plays=sample_plays
    )


@pytest.fixture
def empty_game() -> Game:
    """Provides a Game object with an empty list of plays."""
    return Game(
        game_id='2023_EMPTY_GAME',
        home_team='HOME',
        away_team='AWAY',
        plays=[]
    )


def test_play_creation():
    """Tests basic creation of a Play object."""
    play = Play(posteam='NE', down=1)
    assert play.posteam == 'NE'
    assert play.down == 1
    assert play.third_down_converted is False
    assert play.third_down_failed is False


def test_play_creation_defaults():
    """Tests creating a Play object with default values."""
    play = Play()
    assert play.posteam is None
    assert play.down is None
    assert play.third_down_converted is False
    assert play.third_down_failed is False


def test_game_creation(sample_game: Game, sample_plays: List[Play]):
    """Tests basic creation of a Game object."""
    assert sample_game.game_id == '2023_01_KC_SF'
    assert sample_game.home_team == 'KC'
    assert sample_game.away_team == 'SF'
    assert sample_game.plays == sample_plays


def test_game_len(sample_game: Game):
    """Tests the __len__ method of the Game object."""
    assert len(sample_game) == 6


def test_empty_game_len(empty_game: Game):
    """Tests the __len__ method on a game with no plays."""
    assert len(empty_game) == 0


def test_game_getitem_int(sample_game: Game, sample_plays: List[Play]):
    """Tests integer-based indexing on the Game object."""
    assert sample_game[0] == sample_plays[0]
    assert sample_game[2] == sample_plays[2]


def test_empty_game_getitem_int(empty_game: Game):
    """Tests integer-based indexing on an empty game, expecting an error."""
    with pytest.raises(IndexError):
        _ = empty_game[0]


def test_game_getitem_str_valid(sample_game: Game):
    """Tests string-based key access on the Game object to get play attributes."""
    downs = sample_game['down']
    assert downs == [1, 2, 3, 1, 2, 3]

    posteams = sample_game['posteam']
    assert posteams == ['KC', 'KC', 'KC', 'SF', 'SF', 'SF']


def test_empty_game_getitem_str(empty_game: Game):
    """Tests string-based key access on an empty game."""
    assert empty_game['down'] == []


def test_game_getitem_str_invalid_key(sample_game: Game):
    """Tests string-based key access with an invalid key, expecting an error."""
    with pytest.raises(KeyError, match="'invalid_key' is not a valid attribute on the Play model."):
        _ = sample_game['invalid_key']


def test_game_getitem_invalid_type(sample_game: Game):
    """Tests indexing with an invalid type, expecting an error."""
    with pytest.raises(TypeError, match="Index must be an integer or a string key."):
        _ = sample_game[1.0]


def test_game_iteration(sample_game: Game, sample_plays: List[Play]):
    """Tests iteration over the Game object."""
    iterated_plays = [play for play in sample_game]
    assert iterated_plays == sample_plays


def test_empty_game_iteration(empty_game: Game):
    """Tests iteration over an empty game."""
    iterated_plays = [play for play in empty_game]
    assert iterated_plays == []