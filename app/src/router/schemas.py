from pydantic import BaseModel, Field, validator


class MatchIn(BaseModel):
    player_name: str
    match_name: str
    max_players: int = Field(None, ge=4, le=12)
    min_players: int = Field(None, ge=4, le=12)

    @validator("min_players")
    def less_equal(cls, v, values):
        if v > values["max_players"]:
            raise ValueError("max_players must be greater than or equal to min_players")
        return v


class MatchOut(BaseModel):
    id: int
    nombre: str
    dueño: int
    resultado: str
