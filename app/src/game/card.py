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
