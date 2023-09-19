from pydantic import BaseModel, Field, validator


class PartidaIn(BaseModel):
    nombre_jugador: str
    nombre_partida: str
    nro_max_jugadores: int = Field(None, ge=4, le=12)
    nro_min_jugadores: int = Field(None, ge=4, le=12)

    @validator("nro_min_jugadores")
    def nro_min_menor_o_igual_a_nro_max(cls, v, values):
        if v > values["nro_max_jugadores"]:
            raise ValueError(
                "nro_max_jugadores debe ser mayor o igual a nro_min_jugadores"
            )
        return v


class PartidaOut(BaseModel):
    id: int
    nombre: str
    dueño: int
    resultado: str
