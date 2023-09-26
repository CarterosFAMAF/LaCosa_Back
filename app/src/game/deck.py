from app.src.game.constants import DECK
   

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