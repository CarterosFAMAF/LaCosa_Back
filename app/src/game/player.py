from match import Match
from app.src.game.card import Card
from pony.orm import *
from src.models.models import *
from pydantic import BaseModel
from app.src.router.match_connection_manager import MatchConnectionManager

class Player (BaseModel):
    id : None              #Por ahora podria asignar el id por orden de entrada.
    name : str
    match : Match
    websocket : WebSocket

    def __init__(self, name , match_id):
        player_db = Player_db(
            nombre = name,
            position = 0,
            rol = None,
            match = match_id,
            cartas = None,
            websocket = MatchConnectionManager()
        )
        commit()
        
        self.id = player_db.id
        self.name = name
        self.match = player_db.match
        self.websocket = MatchConnectionManager()
    
