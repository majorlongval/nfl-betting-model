from typing import Dict
from .pbp_data_models import Game, TeamSide, TouchdownType

def _touchdowns(game: Game, type: TouchdownType) -> Dict[TeamSide, int]:
    home_total = 0
    away_total = 0

    for play in game.plays:
        # Check if touchdown_info exists and its type matches
        if play.touchdown and play.touchdown.type == type:
            if play.touchdown.scoring_team == TeamSide.HOME:
                home_total += 1
            elif play.touchdown.scoring_team == TeamSide.AWAY:
                away_total += 1
    return {TeamSide.HOME: home_total, TeamSide.AWAY: away_total}

def passing_touchdowns(game: Game) -> Dict[TeamSide, int]:
    return _touchdowns(game, TouchdownType.PASSING)

def rushing_touchdowns(game: Game) -> Dict[TeamSide, int]:
    return _touchdowns(game, TouchdownType.RUSHING)

def defence_touchdowns(game: Game) -> Dict[TeamSide, int]:
    return _touchdowns(game, TouchdownType.DEFENCE)

def special_teams_touchdowns(game: Game) -> Dict[TeamSide, int]:
    return _touchdowns(game, TouchdownType.SPECIAL_TEAMS)