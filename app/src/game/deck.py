from pony.orm import *
from app.src.game.constants import DECK
from app.src.models.base import Match as MatchDB
from app.src.models.base import Card as CardDB



def create_deck(player_amount: int):
    deck: []
    
    if player_amount == 4:
        deck = DECK[:35]
    elif player_amount == 5:
        deck = DECK[:39]
    elif player_amount == 6:
        deck = DECK[:54]
    elif player_amount == 7:
        deck = DECK[:63]
    elif player_amount == 8:
        deck = DECK[:69]
    elif player_amount == 9:
        deck = DECK[:88]
    elif player_amount == 10:
        deck = DECK[:95]
    elif player_amount == 11:
        deck = DECK[:108]
    elif player_amount == 12:
        deck = DECK[:108]
    else:
        pass     
    return deck


@db_session
def add_cards_to_deck(match_id : int, player_amount: int):
    match = MatchDB[match_id]
    
    if match.max_players >= player_amount and match.min_players <= player_amount:
        deck = create_deck(player_amount)
        for id in deck:
            card = select(c for c in CardDB if c.card_id == id)[:]
            card_copy = CardDB(
                card_id = card[0].card_id,
                name = card[0].name,
                image = card[0].image
            )
            match.deck.add(card_copy)
        flush()