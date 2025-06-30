from typing import Dict, Tuple
from .pbp_data_models import Game, Play, TeamSide
from .utils import calculate_rate_from_plays, flip_perspectives

def third_down_conversion_rate(game: Game) -> Dict[TeamSide, float]:
    """Calculates the third down conversion rate for each team."""
    def processor(play: Play) -> Tuple[int, int, int, int]:
        if play.down == 3:
            success = int(play.third_down_converted)
            failure = int(play.third_down_failed)
            if play.posteam == game.home_team:
                return (success, failure, 0, 0)
            if play.posteam == game.away_team:
                return (0, 0, success, failure)
        return (0, 0, 0, 0)
    return calculate_rate_from_plays(game, processor)

def fourth_down_conversion_rate(game: Game) -> Dict[TeamSide, float]:
    """Calculates the fourth down conversion rate for each team."""
    def processor(play: Play) -> Tuple[int, int, int, int]:
        if play.down == 4:
            success = int(play.fourth_down_converted)
            failure = int(play.fourth_down_failed)
            if play.posteam == game.home_team:
                return (success, failure, 0, 0)
            if play.posteam == game.away_team:
                return (0, 0, success, failure)
        return (0, 0, 0, 0)
    return calculate_rate_from_plays(game, processor)

def third_down_conversion_rate_allowed(game: Game) -> Dict[TeamSide, float]:
    """Calculates the third down conversion rate allowed by each team's defense."""
    offensive_rates = third_down_conversion_rate(game)
    return flip_perspectives(offensive_rates)

def fourth_down_conversion_rate_allowed(game: Game) -> Dict[TeamSide, float]:
    """Calculates the fourth down conversion rate allowed by each team's defense."""
    offensive_rates = fourth_down_conversion_rate(game)
    return flip_perspectives(offensive_rates)