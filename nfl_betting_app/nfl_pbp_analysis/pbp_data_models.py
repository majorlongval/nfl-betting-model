from pydantic import BaseModel

from typing import Iterator, Optional, Union, List, Any
from enum import Enum

class TeamSide(Enum):
    HOME = "HOME"
    AWAY = "AWAY"

class TouchdownType(Enum):
    PASSING = "PASSING"
    RUSHING = "RUSHING"
    DEFENCE = "DEFENCE"
    SPECIAL_TEAMS = "SPECIAL"

class Touchdown(BaseModel):
    type: TouchdownType
    scoring_team: TeamSide
    player_name: Optional[str] = None

class Play(BaseModel):
    posteam: Optional[str] = None
    down: Optional[int] = None
    touchdown: Optional[Touchdown] = None
    third_down_converted: bool = False
    third_down_failed: bool = False
    fourth_down_converted: bool = False
    fourth_down_failed: bool = False
    rushing_yards: Optional[float] = None
    passing_yards: Optional[float] = None

class Game(BaseModel):
    game_id: str
    home_team: str
    away_team: str
    plays: List[Play]

    def __len__(self) -> int:
        return len(self.plays)
        
    def __getitem__(self, key: Union[int, str]) -> Any:
        if isinstance(key, int):
            return self.plays[key]
        elif isinstance(key, str):
            if key not in Play.model_fields:
                raise KeyError(f"'{key}' is not a valid attribute on the Play model.")
            return [getattr(play, key) for play in self.plays]
        else:
            raise TypeError("Index must be an integer or a string key.")

    def __iter__(self) -> Iterator[Play]:
        """
        Allows iterating through the plays of the game, e.g., `for play in game:`.
        """
        yield from self.plays
