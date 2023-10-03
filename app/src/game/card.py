from fastapi import WebSocket
from src.models.base import Player as PlayerDB , Card , Match
from pony.orm import *
from src.game.player import *
from src.game.match import *
from app.src.game.constants import *

class Card:
    name: str

def play_card(player_in,player_out,match_id,card_id)
    if card_id == LANZALLAMAS:
        play_lanzallamas(player_out)
        msg_to_action(player_in,player_out,match_id,"LANZALLAMAS")
        check_finish(match_id)
    else:
        pass
    discard_card_of_player(player_in)

def play_lanzallamas(player_target_id):
    with db_session:
        player_target = Player.get_player_by_id(player_target_id)
        player_target.role = "dead"
        #verificar si esta muerto.
        flush()
        #verificar si hay un minimo de dos jugadores.

    #para los turnos podriamos hacer usar listas , seria mucho mas sencillo.

#probablemente este de mas pero esto avisa sobre la accion que se cometió.
async def msg_to_action(player_in_id,player_out_id,match_id,effect):
    match = get_live_match_by_id(match_id)
    manager = match._match_connection_manager
    player_in = get_player_by_id(player_in_id)
    player_out = get_player_by_id(player_out_id)

    if effect == "LANZALLAMAS":
        msg = f"{player_in.name} calzinó a {player_out.name}"
        status = 8
    else:
        pass
    #aca va a ir todo los mensajes que tengan que ver con los efectos de cartas.
    msg_ws = create_ws_message(match_id,status,msg)
    manager.broadcast_json(msg_ws)