import json

from fastapi import WebSocket


class MatchConnectionManager:
    def __init__(self):
        self.active_connections: list[(int, WebSocket)] = []

    async def connect(self, websocket: WebSocket, player_id: int):
        await websocket.accept()
        conn = (player_id, websocket)
        self.active_connections.append(conn)

        # send welcome json
        welcome_json = json.dumps(
            {"status": 4, "message": "Bienvenido a la partida", "match_data": {}}
        )
        await conn[1].send_json(welcome_json)

    async def disconnect(self, websocket: WebSocket):
        for conn in self.active_connections:
            if websocket in conn:
                self.active_connections.remove(conn)
                break

    async def broadcast_json(self, status: int, msg: str, match_data):
        data = json.dumps({"status": status, "message": msg, "match_data": match_data})

        for conn in self.active_connections:
            try:
                await conn[1].send_json(data)
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
