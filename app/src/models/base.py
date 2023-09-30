from pony.orm import *


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


class Player(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    position = Optional(int)
    role = Optional(str)
    match = Optional(Match, reverse="players")
    match_owner = Optional(Match, reverse="player_owner")


def define_database_and_entities():
    global db

    db.bind(provider="sqlite", filename="the_thing-db.sqlite", create_db=True)
    db.generate_mapping(create_tables=True)
