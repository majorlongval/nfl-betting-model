# nfl_pbp_analysis/__init__.py

# Expose the data models and factory at the top level of the library
from .pbp_data_models import Game, Play, Touchdown, TeamSide, TouchdownType
from .pbp_data_models_factories import game_from_single_game_dataframe

# Expose the analysis functions
from .score_analysis import (
    passing_touchdowns,
    rushing_touchdowns,
    defence_touchdowns,
    special_teams_touchdowns,
    passing_touchdowns_allowed,
    rushing_touchdowns_allowed
)
from .game_statistics import (
    calculate_rushing_yards_per_game,
    calculate_passing_yards_per_game,
    calculate_rushing_yards_allowed_per_game,
    calculate_passing_yards_allowed_per_game
)
from .down_conversion_rate import (
    third_down_conversion_rate,
    fourth_down_conversion_rate,
    third_down_conversion_rate_allowed,
    fourth_down_conversion_rate_allowed
)