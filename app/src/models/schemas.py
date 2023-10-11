from fastapi import HTTPException, status
from pydantic import BaseModel, Field, model_validator , constr



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


class JoinMatchIn(BaseModel):
    player_name: constr(min_length=3, max_length=20)
    match_id: int = Field(ge=1)


class JoinMatchOut(BaseModel):
    player_id: int
    match_name: str

class CardModel(BaseModel):
    card_id: int
    name: str
    image: str
    
class StartMatchIn(BaseModel):
    player_id: int
    match_id: int
