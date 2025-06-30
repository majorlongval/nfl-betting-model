from typing import Callable, Tuple, Union, Dict, Optional
from .pbp_data_models import Game, Play, TeamSide

def aggregate_game_stats(
    game: Game,
    play_processor: Callable[[Play], Tuple[Union[int, float], Union[int, float]]]
) -> Dict[TeamSide, float]:
    """
    Generic aggregator to process all plays in a game and sum the results for home and away teams.

    Args:
        game: The Game object to process.
        play_processor: A function that takes a single `Play` object and returns a
                        tuple of (home_value, away_value) for that play.

    Returns:
        A dictionary with the total summed values for TeamSide.HOME and TeamSide.AWAY.
    """
    home_total = 0.0
    away_total = 0.0

    for play in game.plays:
        home_val, away_val = play_processor(play)
        home_total += home_val
        away_total += away_val

    return {TeamSide.HOME: home_total, TeamSide.AWAY: away_total}

def count_plays_for_team(
    game: Game,
    predicate: Callable[[Play], bool],
    team_identifier: Callable[[Play], Optional[TeamSide]]
) -> Dict[TeamSide, int]:
    """
    Counts plays for each team where a given predicate is true.

    Args:
        game: The Game object to process.
        predicate: A function that returns True if the play should be counted.
        team_identifier: A function that returns the TeamSide responsible for the play.

    Returns:
        A dictionary with the total counts for each team.
    """
    def processor(play: Play) -> Tuple[int, int]:
        if predicate(play):
            team = team_identifier(play)
            if team == TeamSide.HOME:
                return (1, 0)
            if team == TeamSide.AWAY:
                return (0, 1)
        return (0, 0)

    return aggregate_game_stats(game, processor)

def sum_offense_stat_for_team(game: Game, stat_attribute: str) -> Dict[TeamSide, float]:
    """Sums a given stat attribute for the possessing team (posteam)."""

    def processor(play: Play) -> Tuple[float, float]:
        value = getattr(play, stat_attribute) or 0.0
        if play.posteam == game.home_team:
            return (value, 0.0)
        if play.posteam == game.away_team:
            return (0.0, value)
        return (0.0, 0.0)

    return aggregate_game_stats(game, processor)

def calculate_rate_from_plays(
    game: Game,
    play_processor: Callable[[Play], Tuple[int, int, int, int]]
) -> Dict[TeamSide, float]:
    """
    Generic helper to calculate a rate from successes and failures.
    The play_processor should return a tuple of (home_success, home_failure, away_success, away_failure).
    """
    home_successes, home_failures, away_successes, away_failures = 0, 0, 0, 0

    for play in game:
        h_s, h_f, a_s, a_f = play_processor(play)
        home_successes += h_s
        home_failures += h_f
        away_successes += a_s
        away_failures += a_f

    home_total_attempts = home_successes + home_failures
    away_total_attempts = away_successes + away_failures

    home_rate = home_successes / home_total_attempts if home_total_attempts > 0 else 0.0
    away_rate = away_successes / away_total_attempts if away_total_attempts > 0 else 0.0

    return {TeamSide.HOME: home_rate, TeamSide.AWAY: away_rate}

def flip_perspectives(stats: Dict[TeamSide, Union[float, int]]) -> Dict[TeamSide, Union[float, int]]:
    """
    Swaps the home and away values in a stats dictionary.
    Used to convert an offensive stat into a defensive (allowed) stat.
    """
    return {
        TeamSide.HOME: stats[TeamSide.AWAY],
        TeamSide.AWAY: stats[TeamSide.HOME]
    }