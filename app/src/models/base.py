from pony.orm import *
from app.src.game.constants import *

db = Database()

class Match(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    owner = Required("Player")
    started = Required(bool)
    finished = Required(bool)
    turn = Required(int)
    max_players = Required(int)
    min_players = Required(int)
    players = Set("Player")
    deck = Set("Card", reverse="match")
    discard_pile = Set("Card", reverse="match_discard")


class Card(db.Entity):
    """
    Tabla donde guardar las cartas
    """
    id = Required(int, min=1 , max=110)
    name = Required(str)
    image = Required(str, unique=True)
    
    

def define_database_and_entities():
    global db

    db.bind(provider='sqlite', filename='the_thing-db.sqlite', create_db=True)
    db.generate_mapping(create_tables=True)


@db_session
def load_cards():
    try:
        exists_card = db.exists("select * from Card where name=lanzallamas")
        if not exists_card:
            Card(
                id = LANZALLAMAS,
                name = "lanzallamas",
                image = "app/cards/lanzallamas.jpg"
            )
    except:
        pass
    

