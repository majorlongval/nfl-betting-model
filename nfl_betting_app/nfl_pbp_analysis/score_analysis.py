from typing import Dict
from .pbp_data_models import Game, TeamSide, TouchdownType
from .utils import count_plays_for_team, flip_perspectives

def passing_touchdowns(game: Game) -> Dict[TeamSide, int]:
    return count_plays_for_team(
        game,
        predicate=lambda play: play.touchdown is not None and play.touchdown.type == TouchdownType.PASSING,
        team_identifier=lambda play: play.touchdown.scoring_team if play.touchdown else None
    )

def rushing_touchdowns(game: Game) -> Dict[TeamSide, int]:
    return count_plays_for_team(
        game,
        predicate=lambda play: play.touchdown is not None and play.touchdown.type == TouchdownType.RUSHING,
        team_identifier=lambda play: play.touchdown.scoring_team if play.touchdown else None
    )

def defence_touchdowns(game: Game) -> Dict[TeamSide, int]:
    return count_plays_for_team(
        game,
        predicate=lambda play: play.touchdown is not None and play.touchdown.type == TouchdownType.DEFENCE,
        team_identifier=lambda play: play.touchdown.scoring_team if play.touchdown else None
    )

def special_teams_touchdowns(game: Game) -> Dict[TeamSide, int]:
    return count_plays_for_team(
        game,
        predicate=lambda play: play.touchdown is not None and play.touchdown.type == TouchdownType.SPECIAL_TEAMS,
        team_identifier=lambda play: play.touchdown.scoring_team if play.touchdown else None
    )

def passing_touchdowns_allowed(game: Game) -> Dict[TeamSide, int]:
    return flip_perspectives(passing_touchdowns(game))

def rushing_touchdowns_allowed(game: Game) -> Dict[TeamSide, int]:
    return flip_perspectives(rushing_touchdowns(game))