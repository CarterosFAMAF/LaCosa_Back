from pony.orm import *


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


# Conecta a la base de datos SQLite en el archivo 'database.sqlite'
db.bind(provider="sqlite", filename="database.sqlite", create_db=True)

# Genera las tablas en la base de datos
db.generate_mapping(create_tables=True)
