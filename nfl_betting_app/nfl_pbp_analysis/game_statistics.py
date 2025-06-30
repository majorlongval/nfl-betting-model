from typing import Dict, Union
from .pbp_data_models import Game, TeamSide
from .utils import sum_offense_stat_for_team, flip_perspectives

def calculate_rushing_yards_per_game(game: Game) -> Dict[TeamSide, float]:
    """Calculates total rushing yards for each team in a game."""
    return sum_offense_stat_for_team(game, 'rushing_yards')

def calculate_passing_yards_per_game(game: Game) -> Dict[TeamSide, float]:
    """Calculates total passing yards for each team in a game."""
    return sum_offense_stat_for_team(game, 'passing_yards')

def calculate_rushing_yards_allowed_per_game(game: Game) -> Dict[TeamSide, float]:
    """Calculates total rushing yards allowed by each team in a game."""
    offensive_yards = calculate_rushing_yards_per_game(game)
    return flip_perspectives(offensive_yards)

def calculate_passing_yards_allowed_per_game(game: Game) -> Dict[TeamSide, float]:
    """Calculates total passing yards allowed by each team in a game."""
    offensive_yards = calculate_passing_yards_per_game(game)
    return flip_perspectives(offensive_yards)