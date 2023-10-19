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


def play_card(player_in, player_out, match_id: int, card_id: int):
    """
    Play a card from a player to another player, changes the state of the game, and send a message to all players

    Args:
        player_in (Player)
        player_out (Player)
        match_id (int)
        card_id (int)

    Returns:
        None
    """
    card = get_card_by_id(card_id)
    assert card is not None
    status = None
    
    if card.card_id == LANZALLAMAS:   
        status = play_lanzallamas(player_out.id)
    if card.card_id == MAS_VALE_QUE_CORRAS:
        status = play_mas_vale_que_corras(player_in.id,player_out.id)
    if card.card_id == VIGILA_TUS_ESPALDAS:
        status = play_vigila_tus_espaldas(match_id)
    else:
        pass

    discard_card_of_player(card.id, match_id, player_in.id)
    return status

def play_lanzallamas(player_target_id):
    """
    Set the role of a player to dead

    Args:
        player_target_id (int)

    Returns:
        None
    """
    with db_session:
        player_target = get_player_by_id(player_target_id)
        player_target.role = "dead"
        flush()
    status = WS_STATUS_PLAYER_BURNED
    return status
    
def play_sospecha(player_id,player_target_id,match_id):
    """
    return name of card random of player target

    Args:
        player_target_id (int)

    Returns:
        name of card
    """
    with db_session:
        match = get_live_match_by_id(match_id)
        player_target = get_player_by_id(player_target_id)
        card_random = player_target.hand.random(1).first()
        
        #al player deberia mandarle que carto tiene el jugador objetivo
        status = WS_STATUS_CARD_DISCOVER
        msg_ws = create_ws_message(match_id,status,player_id,player_target_id,card_random.id)
        match._match_connection_manager.send_personal_json(msg_ws,player_id)
        
        #al player afectado por la carta le manda un msj de que han visto su carta y cual
        status = WS_STATUS_CARD_SHOWN
        msg_ws = create_ws_message(match_id,status,player_id,player_target_id,card_random.id) 
        match._match_connection_manager.send_personal_json(msg_ws,player_target_id)
        
        status = WS_STATUS_SUSPECT
        return status
    
def play_mas_vale_que_corras(player_main_id,player_target_id):
    # Deberia haber intercambio antes de el cambio de posicion.
    # Cambia el position del player_main y player_target
    """
    reverse the roles of player in turn and player target

    Args:
        player_main_id (int)
        player_target_id (int)

    Returns:
        message of players that change position
    """
    with db_session:
        player_main = get_player_by_id(player_main_id)
        player_target = get_player_by_id(player_target_id)
        pos_tmp = player_main.position
        player_main.position = player_target.position 
        player_target.position = pos_tmp
        flush()
    status = WS_STATUS_CHANGED_OF_PLACES
    return status

def play_vigila_tus_espaldas(match_id):
    """
    reverse all positions of the players

    Args:
        match_id(int)

    Returns:
        message that all positions were reversed
    """
    # Invierte todas las posiciones de los jugadores en la partida
    with db_session:
        match = get_match_by_id(match_id)
        match.clockwise = not match.clockwise
        flush()
        """
        turn = match.turn
        all_players = match.number_players
        
        for player in match.players:
            player.position = ((2 * turn) - player.position) % all_players
            flush()
        """
        
    status = WS_STATUS_REVERSE_POSITION
    return status

def play_card_investigation(player_target,card):
    names = ""
    
    if card.card_id == SOSPECHA:
        card_random = select(c for c in player_target.hand).random(1)[0]
        card_image = get_card_image(card_random.image)
        
    return {"id": card_random.id, "name": card_random.name, "image": card_image}
    