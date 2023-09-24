from pony.orm import *

db = Database()

class Card(db.Entity):
    """
    Tabla donde guardar las cartas
    """
    name = Required(str)
    type = Required(int, min=1 , max=110)
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
                name = "lanzallamas",
                type = 1,
                image = "app/cards/lanzallamas.jpg"
            )
    except:
        pass
    

