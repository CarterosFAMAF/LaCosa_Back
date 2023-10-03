from fastapi import WebSocket
from src.models.base import Player as PlayerDB , Card , Match
from pony.orm import *
from src.game.player import *
from src.game.match import *
from app.src.game.constants import *

class Card:
    name: str

def play_card(player_out,match_id,card_id)
    if card_id == LANZALLAMAS:
        play_lanzallamas(player_out,match_id,card_id)
    else:
        pass
    match = get_live_match_by_id(match_id)
    match.next_turn()
    

def play_lanzallamas(player_target_id):
    with db_session:
        player_target = Player.get_player_by_id(player_target_id)
        player_target.role = "dead"
        #verificar si esta muerto.
        flush()
        #abria que cambiar como van los turnos

        #para los turnos podriamos hacer usar listas , seria mucho mas sencillo.
