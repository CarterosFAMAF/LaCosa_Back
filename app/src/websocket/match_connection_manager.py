import json

from fastapi import WebSocket
from pony.orm import *

from app.src.models.base import Match as MatchDB
from app.src.websocket.constants import *


class MatchConnectionManager:
    def __init__(self):
        self.active_connections: list[(int, WebSocket)] = []

    async def connect(self, websocket: WebSocket, player_id: int, match_id: int):
        """
        Connect a client to a match. Add the client to the list of active connections and send a welcome message to the client

        Args:
            websocket (WebSocket)
            player_id (int)
            match_id (int)

        Returns:
            None
        """

        await websocket.accept()
        conn = (player_id, websocket)
        self.active_connections.append(conn)
        welcome_msg = create_ws_message(match_id, 4, player_id)
        json_msg = json.dumps(welcome_msg)
        await websocket.send_json(json_msg)

    async def disconnect(self, websocket: WebSocket, player_id: int, match_id: int):
        """
        Disconnect a client from a match. Remove the client from the list of active connections

        Args:
            websocket (WebSocket)

        Returns:
            None
        """

        for conn in self.active_connections:
            if websocket in conn:
                self.active_connections.remove(conn)
                break

        # if match is not finished, send message to all players
        with db_session:
            match_db = MatchDB.get(id=match_id)
            if match_db != None:
                if match_db.finalized == False:
                    data_ws = create_ws_message(
                        match_id, WS_STATUS_PLAYER_LEFT, player_id
                    )
                    await self.broadcast_json(data_ws)

    async def broadcast_json(self, data: dict):
        """
        Send a json message to all clients connected to a match

        Args:
            data (dict)

        Returns:
            None
        """

        # transform data to json
        json_data = json.dumps(data)

        for conn in self.active_connections:
            try:
                await conn[1].send_json(json_data)
            except:
                self.active_connections.remove(conn)

    async def send_personal_json(self, data: dict, player_id: int):
        """
        Send a json message to a specific client

        Args:
            data (dict)
            player_id (int)

        Returns:
            None
        """

        json_data = json.dumps(data)
        for conn in self.active_connections:
            if player_id in conn:
                try:
                    await conn[1].send_json(json_data)
                except:
                    self.active_connections.remove(conn)


def create_ws_message(
    match_id: int, status: int, player_id: int = 0, player_target_id: int = 0, card_name: str = ""
):
    """
    Create a dictionary to then send as a json message to the client. Utilizes the state of the match in the db

    Args:
        match_id (int)
        status (int)
        player_id (int) Optional
        player_target_id (int) Optional

    Returns:
        match_ws (dict)
    """
    match_ws = None
    with db_session:
        match_db = MatchDB.get(id=match_id)
        players = []
        player_name = ""
        player_target_name = ""
        
        for player in match_db.players:
            # get player names to make the msg, if there isn't player_id or player_target_id, set to None
            if player_id > 0 and player.id == player_id:
                player_name = player.name

            if player_target_id > 0 and player.id == player_target_id:
                player_target_name = player.name
                        
            # add player to the list of players
            players.append(
                {
                    "id": player.id,
                    "name": player.name,
                    "turn": player.position,
                    "alive": True if player.role != "dead" else False,
                }
            )
        # sort players by turn
        players.sort(key=lambda x: x["turn"])
        msg = get_ws_message_with_status(status, player_name, player_target_name,card_name)

        match_ws = {
            "player_id": player_id,
            "player_target_id": player_target_id,
            "status": status,
            "message": msg,
            "started": match_db.started,
            "turn_game": match_db.turn,
            "players": players,
        }
    return match_ws


def get_ws_message_with_status(status: int, player_name: str, player_target_name: str, card_name: str):
    """
    Returns the message associated with a status code

    Args:
        status (int)
        player_name (str) Optional
        player_target_name (str) Optional

    Returns:
        message (str)
    """

    message = ""

    if status == WS_STATUS_PLAYER_JOINED:
        message = f"{player_name} se unio a la partida"
    elif status == WS_STATUS_PLAYER_LEFT:
        message = f"{player_name} abandono la partida"
    elif status == WS_STATUS_MATCH_STARTED:
        message = "La partida comenzo"
    elif status == WS_STATUS_MATCH_ENDED:
        message = "La partida finalizo"
    elif status == WS_STATUS_PLAYER_WELCOME:
        message = f"Bienvenido a la partida {player_name}"
    elif status == WS_STATUS_NEW_TURN:
        message = f"Turno nuevo de {player_name}"
    elif status == WS_STATUS_PLAYER_BURNED:
        message = f"{player_name} calzino {player_target_name}"
    elif status == WS_STATUS_HUMANS_WIN:
        message = "Los Humanos ganan"
    elif status == WS_STATUS_INFECTEDS_WIN:
        message = "Los Infectados ganan"
    elif status == WS_STATUS_THE_THING_WIN:
        message = "La cosa gana"
    elif status == WS_STATUS_CHANGED_OF_PLACES:
        message = f"{player_name} intercambio lugar con {player_target_name}"
    elif status == WS_STATUS_REVERSE_POSITION:
        message = f"se han inviertido todas las posiciones"
    elif status == WS_STATUS_DISCARD:
        message = f"{player_name} ha descartado una carta"
    elif status == WS_STATUS_SUSPECT:
        message = f"{player_name} ha jugado una carta sospecha sobre {player_target_name}"
    elif status == WS_STATUS_CARD_DISCOVER:
        message = f"se descubrió que {player_target_name} tenia una carta {card_name}"
    elif status == WS_STATUS_CARD_SHOWN:
        message = f"tu carta {card_name} ha sido vista por {player_name}"
    elif status == WS_STATUS_ANALYSIS:
        message = f"{player_name} ha analizado las cartas de {player_target_name}"
    elif status == WS_STATUS_WHISKY:
        message = f"{player_name} ha mostrado todas sus cartas"
    else:
        message = "Status desconocido"  # Handle unknown status values
    return message