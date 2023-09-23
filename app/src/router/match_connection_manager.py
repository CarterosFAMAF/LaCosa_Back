from fastapi import WebSocket
from src.game.player import Player


class MatchConnectionManager:
    def __init__(self):
        self.active_connections: list[Player] = []

    """
    async def difundir(self, mensaje: dict):
        for jugador in self.jugadores:
            await jugador.websocket.send_json(mensaje)

    async def conectar_jugador(self, websocket: WebSocket, jugador_id: int):
        await websocket.accept()
        self.jugadores[jugador_id].websocket = websocket
        await self.difundir(self.dict())
    """
