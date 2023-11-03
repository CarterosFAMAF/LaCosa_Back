from fastapi import HTTPException, status
from pydantic import BaseModel, Field, model_validator, constr


class MatchIn(BaseModel):
    player_name: str
    # match name not empty and string
    match_name: constr(min_length=1, max_length=100)
    min_players: int = Field(ge=4, le=12)
    max_players: int = Field(ge=4, le=12)

    @model_validator(mode="after")
    def check_min_max_players(self) -> "MatchIn":
        min_players = self.min_players
        max_players = self.max_players
        if min_players > max_players:
            raise HTTPException(
                {
                    "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                    "detail": "min_players must be less than max_players",
                }
            )
        return self


class MatchOut(BaseModel):
    match_id: int
    owner_id: int
    result: str


class ExchangeCardIn(BaseModel):
    match_id: int
    player_id: int
    player_target_id: int
    card_id: int


class ListMatchOut(BaseModel):
    match_id: int
    match_name: str
    owner_name: str
    player_count: int
    player_min: int
    player_max: int
    joined_players: list


class JoinMatchIn(BaseModel):
    player_name: constr(min_length=1, max_length=100)
    match_id: int = Field(ge=1)


class JoinMatchOut(BaseModel):
    player_id: int
    match_name: str


class CardModel(BaseModel):
    id: int = 0
    name: str = ""
    image: str = ""


class PlayCardModel(BaseModel):
    match_id: int
    player_in_id: int
    player_out_id: int
    card_id: int


class StartMatchIn(BaseModel):
    player_id: int
    match_id: int


class DiscardIn(BaseModel):
    card_id: int
    player_id: int
    match_id: int
