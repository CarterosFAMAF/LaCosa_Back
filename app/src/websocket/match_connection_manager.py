import json

from fastapi import WebSocket
from pony.orm import *

from app.src.models.base import Match as MatchDB
from app.src.websocket.constants import *
from app.src.game.player import get_player_by_id


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


def create_msg_revelations(hand):
    
    response = {
        "status" : WS_STATUS_REVELATIONS,
        "hand" : hand
    }
    
    return response 

def create_msg_defense(player_main_id, card_id, card_name, list_id_cards_def):
    # que mando en el mensaje: status,id de player que activo carta accion,card id, ids de cartas defense del objetivo

    with db_session:
        player = get_player_by_id(player_main_id)
        player_name = player.name

    if card_id == 0:
        message = (
            f"{player_name} intenta intercambiar cartas contigo, ¿Quieres defenderte?"
        )

    else:
        message = f"{player_name} intenta utilizar {card_name} en tu contra, ¿Quieres defenderte?"

    data_for_defense = {
        "player_id": player_main_id,
        "card_main_id": card_id,
        "defensive_options_id": list_id_cards_def,
        "message": message,
    }

    response = {
        "status": WS_STATUS_DEFENSE_PRIVATE_MSG,
        "data_for_defense": data_for_defense,
    }

    return response


def create_ws_chat_message(player_id: int = 0, msg: str = ""):
    """
    Create dictionary to then send it as a json messege to the client. Utilizes state of the match in the db

    Args:
        player_id (int)
        msg (str)

    Returns:
        msg_ws (dict)
    """

    player = get_player_by_id(player_id)
    player_name = player.name

    msg_ws = {
        "status": WS_STATUS_CHAT_MESSAGE,
        "msg": {"owner": player_name, "text": msg},
    }

    return msg_ws


def create_ws_message_fallaste(
    player_main_id: int = 0, player_fallaste_id: int = 0, player_target_id: int = 0
):
    """
    Create dictionary to then send it as a json messege to the client. Utilizes state of the match in the db

    Args:
        player_main (int)
        player_fallaste (int)
        player_target (int)

    Returns:
        msg_ws (dict)
    """

    player_main = get_player_by_id(player_main_id)
    player_fallaste = get_player_by_id(player_fallaste_id)
    player_target = get_player_by_id(player_target_id)

    player_main_name = player_main.name
    player_fallaste_name = player_fallaste.name
    player_target_name = player_target.name

    msg_ws = {
        "status": WS_STATUS_YOU_FAILED,
        "message": f"{player_fallaste_name} hizo fallar el intercambio de {player_main_name}. Ahora le toca a {player_target_name}",
        "player_main_id": player_main_id,
        "player_fallaste": player_fallaste_id,
        "player_target": player_target_id,
    }

    return msg_ws


    
    return response

def create_ws_message(
    match_id: int,
    status: int,
    player_id: int = 0,
    player_target_id: int = 0,
    card_name: str = "",
    list_revealed_card: list = [],
):
    """
    Create a dictionary to then send it as a json message to the client. Utilizes the state of the match in the db

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
                    "quarantine": player.quarantine,
                    "winner": player.winner,
                    "revealed_cards": list_revealed_card
                    if player.id == player_id
                    else [],
                }
            )
        # sort players by turn
        players.sort(key=lambda x: x["turn"])
        msg = get_ws_message_with_status(
            status, player_name, player_target_name, card_name
        )

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


def get_ws_message_with_status(
    status: int, player_name: str, player_target_name: str, card_name: str
):
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
    # Lobby
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
    # Partida
    elif status == WS_STATUS_NEW_TURN:
        message = f"Turno nuevo de {player_name}"
    elif status == WS_STATUS_DISCARD:
        message = f"{player_name} ha descartado una carta"
    elif status == WS_STATUS_EXCHANGE:
        message = f"{player_name} ha realizado un intercambio con {player_target_name}"
    elif status == WS_STATUS_EXCHANGE_REQUEST:
        message = f"{player_name} ha solicitado un intercambio a {player_target_name}"
    elif status == WS_STATUS_INFECTED:
        message = f"{player_name} te ha infectado"
    elif status == WS_STATUS_HUMANS_WIN :
        message = "Ganan los humanos"
    elif status == WS_STATUS_INFECTEDS_WIN:
        message = "Gana La Cosa junto a los infectados"
    elif status == WS_STATUS_THE_THING_WIN:
        message = "Gana La cosa"
    elif status == WS_STATUS_YES:
        message = f"{player_name} decidio mostrar sus cartas"
    elif status == WS_STATUS_NOPE:
        message = f"{player_name} prefiere no mostrar sus cartas"
    # Accion
    elif status == WS_STATUS_SUSPECT:
        message = f"{player_name} sospecha de {player_target_name}"
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
        message = f"Ha cambiado el sentido de la ronda"
    elif status == WS_STATUS_CARD_DISCOVER:
        message = f"Se descubrio que {player_target_name} tenia una carta {card_name}"
    elif status == WS_STATUS_CARD_SHOWN:
        message = f"Tu carta {card_name} ha sido vista por {player_name}"
    elif status == WS_STATUS_ANALYSIS:
        message = f"{player_name} ha analizado las cartas de {player_target_name}"
    elif status == WS_STATUS_WHISKY:
        message = f"{player_name} ha mostrado todas sus cartas"
    elif status == WS_STATUS_SEDUCCION:
        message = (
            f"{player_name} ha seducido a {player_target_name} para intercambiar cartas"
        )
    elif status == WS_STATUS_DETERMINATION:
        message = f"{player_name} esta determinado a sobrevivir"
    elif status == WS_STATUS_AXE:
        message = f"{player_name} rompio la cuarentena de {player_target_name}"
    # Defensa
    elif status == WS_STATUS_HERE_IM_FINE:
        message = f"{player_name} se siente seguro en donde esta"
    elif status == WS_STATUS_NOTHING_BARBECUE:
        message = (
            f"{player_name} se ha salvado de ser calzinado por {player_target_name}"
        )
    elif status == WS_STATUS_NOPE_THANKS:
        message = f"{player_name} dice que no al intercambio pero igual lo agradece"
    elif status == WS_STATUS_SCARY:
        message = f"A {player_name} le resulto aterrador el intercambio con {player_target_name}, asi que prefiere evitarlo"
    
    # Panico
    elif status == WS_STATUS_LET_IT_REMAIN_BETWEEN_US:
        message = f"{player_name} le esta susurrando a {player_target_name}"
    elif status == WS_STATUS_UPS:
        message = f"Ups! a {player_name} se le han caido sus cartas"
    elif status == WS_STATUS_BLIND_DATE:
        message = f"A {player_name} le apetece tener una cita a ciegas"
    elif status == WS_STATUS_SHOWS:
        message = f"Estas viendo la mano de {player_name}"
    elif status == WS_STATUS_REVELATIONS:
        message = f"Comienza la ronda de revelaciones"

    # Obstaculo
    elif status == WS_STATUS_QUARANTINE:
        message = f"{player_name} puso en cuarentena a {player_target_name}"
    
    # Cuarentena
    elif status == WS_STATUS_DRAW:
        message = f"{player_name} robo la carta {card_name}"
    elif status == WS_STATUS_EXCHANGE_REQUEST_QUARANTINE:
        message = f"{player_name} ha solicitado un intercambio a {player_target_name} con la carta {card_name}"
    elif status == WS_STATUS_EXCHANGE_QUARANTINE:
        message = f"{player_name} ha realizado un intercambio con {player_target_name} la carta {card_name}"
    elif status == WS_STATUS_DISCARD_QUARANTINE:
        message = f"{player_name} ha descartado la carta {card_name}"
    else:
        message = "Status desconocido"  # Handle unknown status values
    return message
