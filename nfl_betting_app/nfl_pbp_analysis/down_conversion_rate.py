from typing import Dict
from .pbp_data_models import Game, Play, TeamSide

def _calculate_down_conversion_rate_generic(
    game: Game,
    down_number: int,
    converted_attr: str,
    failed_attr: str
) -> Dict[TeamSide, float]:
    home_successes = 0
    home_failures = 0
    away_successes = 0
    away_failures = 0

    for play in game:
        if play.down == down_number:
            is_converted = getattr(play, converted_attr, False)
            is_failed = getattr(play, failed_attr, False)

            if play.posteam == game.home_team:
                home_successes += is_converted
                home_failures += is_failed
            elif play.posteam == game.away_team:
                away_successes += is_converted
                away_failures += is_failed

    home_total_attempts = home_successes + home_failures
    away_total_attempts = away_successes + away_failures

    home_rate = home_successes / home_total_attempts if home_total_attempts > 0 else 0.0
    away_rate = away_successes / away_total_attempts if away_total_attempts > 0 else 0.0

    return {TeamSide.HOME: home_rate, TeamSide.AWAY: away_rate}

def third_down_conversion_rate(game: Game) -> Dict[TeamSide, float]:
    return _calculate_down_conversion_rate_generic(
        game, 3, 'third_down_converted', 'third_down_failed'
    )

def fourth_down_conversion_rate(game: Game) -> Dict[TeamSide, float]:
    return _calculate_down_conversion_rate_generic(
        game, 4, 'fourth_down_converted', 'fourth_down_failed'
    )