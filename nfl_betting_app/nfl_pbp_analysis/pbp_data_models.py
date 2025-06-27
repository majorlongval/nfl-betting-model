from pydantic import BaseModel

from typing import Iterator, Optional, Union, List, Any

class Play(BaseModel):
    posteam: Optional[str] = None
    down: Optional[int] = None
    third_down_converted: bool = False
    third_down_failed: bool = False

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
