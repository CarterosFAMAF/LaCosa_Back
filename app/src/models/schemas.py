from fastapi import HTTPException, status
from pydantic import BaseModel, Field, validator, constr


class MatchIn(BaseModel):
    player_name: str
    # match name not empty and string
    match_name: constr(min_length=1, max_length=100)
    min_players: int = Field(ge=4, le=12)
    max_players: int = Field(ge=4, le=12)

    @validator("min_players", "max_players", pre=True, always=True)
    def check_min_max_players(cls, value, values):
        min_players = values.get("min_players")
        max_players = values.get("max_players")
        if min_players is not None and max_players is not None and min_players > max_players:
            raise HTTPException(
                {
                    "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                    "detail": "min_players must be less than max_players",
                }
            )
        return value


class MatchOut(BaseModel):
    match_id: int
    owner_id: int
    result: str


class ExchangeCardIn(BaseModel):
    match_id: int
    player_id: int
    player_target_id: int
    card_id: int
    is_you_failed:bool=False
    blind_date:bool=False
    
class revelationsIn(BaseModel):
    match_id: int
    player_id: int
    show:bool=False
    

class getCardIn(BaseModel):
    match_id: int
    player_id:int
    not_panic:bool=False

class ListMatchOut(BaseModel):
    match_id: int
    match_name: str
    owner_name: str
    player_count: int
    player_min: int
    player_max: int
    joined_players: list

class GetCardModel(BaseModel):
    match_id: int
    player_id: int
    not_panic:bool=False
    
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
    type: str = ""


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

class declare_endIn(BaseModel):
    match_id:int

class PlayCardDefenseIn(BaseModel):
    player_main_id: int
    match_id: int
    card_main_id: int
    card_target_id: int
    player_target_id: int
