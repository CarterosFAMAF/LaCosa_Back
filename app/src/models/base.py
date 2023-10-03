from pony.orm import *
from app.src.game.constants import *

db = Database()


class Match(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    number_players = Required(int)
    max_players = Required(int)
    min_players = Required(int)
    started = Optional(bool)
    finalized = Optional(bool)
    turn = Optional(int)
    players = Set("Player", reverse="match")
    player_owner = Required("Player", reverse="match_owner")
    deck = Set("Card", reverse="deck")
    discard_pile = Set("Card", reverse="discard_deck")

class Player(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    turn = Optional(int)
    role = Optional(str)
    deck = Set("Card")
    match = Optional(Match, reverse="players")
    match_owner = Optional(Match, reverse="player_owner")


class Card(db.Entity):
    """
    Tabla donde guardar las cartas
    """
    id = PrimaryKey(int, auto=True)
    card_id = Required(int)
    name = Required(str)
    image = Required(str)
    deck = Set(Match, reverse="deck")
    discard_deck = Set(Match, reverse="discard_pile")
  

def define_database_and_entities():
    global db

    db.bind(provider='sqlite', filename='the_thing-db.sqlite', create_db=True)
    db.generate_mapping(create_tables=True)


@db_session
def load_cards():
    try:
        exists_card = db.exists("select * from Card where name='lanzallamas'")
        if not exists_card:
            Card(
                card_id = LANZALLAMAS,
                name = "lanzallamas",
                image = "app/cards/lanzallamas.jpg"
            )
    except:
        pass

