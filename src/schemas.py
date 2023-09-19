from pydantic import BaseModel


class PartidaIn(BaseModel):
    nombre_jugador: str
    nombre_partida: str
    nro_max_jugadores: int
    nro_min_jugadores: int


class PartidaOut(BaseModel):
    id: int
    nombre: str
    dueño: int
    resultado: str
