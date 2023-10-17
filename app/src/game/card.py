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

    if card.card_id == LANZALLAMAS:   
        play_lanzallamas(player_out.id)
    if card.card_id == SOSPECHA:
        play_sospecha(player_out.id)
    if card.card_id == MAS_VALE_QUE_CORRAS:
        play_mas_vale_que_corras(player_in.id,player_out.id)
    if card.card_id == VIGILA_TUS_ESPALDAS:
        play_vigila_tus_espaldas(match_id)
    else:
        pass

    discard_card_of_player(card.id, match_id, player_in.id)


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
        
def play_sospecha(player_target_id):
    #esta funcion deberia devolver alguna carta random del player target
    with db_session:
        player_target = get_player_by_id(player_target_id)
        card_rm = player_target.hand.random(1).first()
        
        return card_rm.name
    
def play_mas_vale_que_corras(player_main_id,player_target_id):
    # Deberia haber intercambio antes de el cambio de posicion.
    # Cambia el position del player_main y player_target
    with db_session:
        player_main = get_player_by_id(player_main_id)
        player_target = get_player_by_id(player_target_id)
        pos_tmp = player_main.position
        player_main.position = player_target.position 
        player_target.position = pos_tmp
        flush()
    
def play_vigila_tus_espaldas(match_id):
    # Invierte todas las posiciones de los jugadores en la partida
    with db_session:
        match = get_match_by_id(match_id)
        num_players = match.number_players - 1
        
        for player in match.players:
            player.position = num_players
            num_players -= 1
    flush()
