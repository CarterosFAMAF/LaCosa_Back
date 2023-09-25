from pydantic import BaseModel, Field, model_validator


class MatchIn(BaseModel):
    player_name: str
    match_name: str
    min_players: int = Field(ge=4, le=12)
    max_players: int = Field(ge=4, le=12)

    @model_validator(mode="after")
    def check_min_max_players(self) -> "MatchIn":
        min_players = self.min_players
        max_players = self.max_players
        if min_players > max_players:
            raise ValueError("min_players must be less than max_players")
        return self


class MatchOut(BaseModel):
    match_id: int
    match_name: str
    owner_id: int
    result: str
