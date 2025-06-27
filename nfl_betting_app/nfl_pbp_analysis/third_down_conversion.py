
from typing import Dict
from pbp_data_models import Game

def calculate_third_down_conversion(game: Game) -> Dict[str, float]:
    home_successes = 0
    home_failures = 0
    away_successes = 0
    away_failures = 0

    for play in game:
        if play.down == 3:
            if play.posteam == game.home_team:
                home_successes += play.third_down_converted
                home_failures += play.third_down_failed
            elif play.posteam == game.away_team:
                away_successes += play.third_down_converted
                away_failures += play.third_down_failed

    home_total_attempts = home_successes + home_failures
    away_total_attempts = away_successes + away_failures

    home_rate = home_successes / home_total_attempts if home_total_attempts > 0 else 0.0
    away_rate = away_successes / away_total_attempts if away_total_attempts > 0 else 0.0

    return {'HOME': home_rate, 'AWAY': away_rate}