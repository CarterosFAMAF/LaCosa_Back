import json

from fastapi import WebSocket
from app.src.models.base import Match as MatchDB
from pony.orm import *


class MatchConnectionManager:
    def __init__(self):
        self.active_connections: list[(int, WebSocket)] = []

    async def connect(self, websocket: WebSocket, player_id: int, match_id: int):
        await websocket.accept()
        conn = (player_id, websocket)
        self.active_connections.append(conn)
        welcome_msg = create_ws_message(match_id, 4, "Bienvenido a la partida")
        json_msg = json.dumps(welcome_msg)
        await websocket.send_json(json_msg)

    async def disconnect(self, websocket: WebSocket):
        for conn in self.active_connections:
            if websocket in conn:
                self.active_connections.remove(conn)
                break

    async def broadcast_json(self, data: dict):
        # transform data to json
        json_data = json.dumps(data)

        for conn in self.active_connections:
            try:
                await conn[1].send_json(json_data)
            except:
                self.active_connections.remove(conn)

    # POR AHORA NO USAR ESTE PLS. SI HAY QUE COMPARTIR ALGO, SE COMPARTE A TODOS E
    async def send_personal_json(self, status: int, msg: str, match_data, jugador_id):
        for conn in self.active_connections:
            if jugador_id in conn:
                try:
                    await conn[1].send_json(
                        {"status": status, "message": msg, "match_data": match_data}
                    )
                except:
                    self.active_connections.remove(conn)


def create_ws_message(match_id: int, status: int, msg: str):
    """
    Create a json message to send to the client. Utilizes the state of the match in the db

    Args:
        match_id (int)
        status (int)
        msg (str)

    Returns:
        match_ws (dict)
    """
    match_ws = None
    with db_session:
        match_db = MatchDB.get(id=match_id)
        players = []
        for player in match_db.players:
            players.append(
                {
                    "id": player.id,
                    "name": player.name,
                    "turn": player.turn,
                    "alive": True if player.role != "dead" else False,
                }
            )
        match_ws = {
            "status": status,
            "message": msg,
            "started": match_db.started,
            "turn_game": match_db.turn,
            "players": players,
        }
    return match_ws


    