from fastapi import WebSocket
from app.src.models.base import Player as PlayerDB 
from app.src.models.base import Card as CardDB
from app.src.models.base import Match as MatchDB
from pony.orm import *
from app.src.game.player import *
from app.src.game.match import *
from app.src.game.constants import *

class Card:
    name: str

def play_card(player_in,player_out,match_id,card_id):
    card = get_card_by_id(card_id)

    if card.card_id == LANZALLAMAS:
        play_lanzallamas(player_out)
        #msg_to_action(player_in,player_out,match_id,"LANZALLAMAS")
        check_finish(match_id)
    else:
        pass
    discard_card_of_player(card.id,match_id,player_in)

def play_lanzallamas(player_target_id):
    with db_session:
        player_target = get_player_by_id(player_target_id)
        player_target.role = "dead"
        flush()

#probablemente este de mas pero esto avisa sobre la accion que se cometió.
async def msg_to_action(player_in_id,player_out_id,match_id,effect):
    match = get_live_match_by_id(match_id)
    manager = match._match_connection_manager
    player_in = get_player_by_id(player_in_id)
    player_out = get_player_by_id(player_out_id)

    if effect == "LANZALLAMAS":
        status = WS_STATUS_PLAYER_BURNED
    else:
        pass
    #aca va a ir todo los mensajes que tengan que ver con los efectos de cartas.
    msg_ws = create_ws_message(match_id,status,player_in.id,player_out.id)
    await manager.broadcast_json(msg_ws)


