from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket, status
from schemas import *

from partida import Partida


app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root
@app.get("/")
async def root():
    return {"message": "La Cosa"}


# Crear partida
@app.post("/partidas", response_model=PartidaOut, status_code=status.HTTP_201_CREATED)
async def crear_partida(partida: PartidaIn) -> int:
    nueva_partida = Partida(
        partida.nombre_jugador,
        partida.nombre_partida,
        partida.nro_max_jugadores,
        partida.nro_min_jugadores,
    )
    return PartidaOut(
        id=nueva_partida.id,
        nombre=nueva_partida.nombre,
        dueño=nueva_partida.dueño.id,
        resultado="Partida creada",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
