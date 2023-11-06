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
    clockwise = Optional(bool)
    players = Set("Player", reverse="match")
    player_owner = Required("Player", reverse="match_owner")
    deck = Set("Card", reverse="deck")
    discard_pile = Set("Card", reverse="discard_deck")


class Player(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    position = Optional(int, default=-1)
    role = Optional(str)
    hand = Set("Card")
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
    player_hand = Set(Player)
    deck = Set(Match, reverse="deck")
    discard_deck = Set(Match, reverse="discard_pile")


def define_database_and_entities(test: bool):
    global db

    if test:
        db.bind(provider="sqlite", filename="test-the_thing-db.sqlite", create_db=True)
    else:
        db.bind(provider="sqlite", filename="the_thing-db.sqlite", create_db=True)
    db.generate_mapping(create_tables=True)


@db_session
def load_cards():
    try:
        exists_card = db.exists("select * from Card where name='lanzallamas'")
        if not exists_card:
            Card(
                card_id=LANZALLAMAS,
                name="lanzallamas",
                image="app/cards/lanzallamas.png",
            )
            Card(
                card_id=LA_COSA,
                name="La_Cosa",
                image="app/cards/LaCosa.png",
            )
            Card(
                card_id = MAS_VALE_QUE_CORRAS,
                name="Mas_Vale_Que_Corras",
                image="app/cards/Mas_vale_que_corras.png",
            )
            Card(
                card_id = SOSPECHA,
                name="Sospecha",
                image="app/cards/sospecha.png",
            )
            Card(
                card_id = VIGILA_TUS_ESPALDAS,
                name="Vigila_Tus_Espaldas",
                image="app/cards/Vigila_tus_espaldas.png",
            )
            Card(
                card_id = WHISKY,
                name="Whisky",
                image="app/cards/Whisky.png",
            )
            Card(
                card_id = ANALISIS,
                name="Analisis",
                image="app/cards/Analisis.png",
            )
            Card(
                card_id = CAMBIO_DE_LUGAR,
                name="Cambio_de_lugar",
                image="app/cards/Cambio_de_lugar.png",
            )
            Card(
                card_id = CUARENTENA,
                name="Cuarentena",
                image="app/cards/Cuarentena.png",
            )
            Card(
                card_id = PUERTA_ATRANCADA,
                name="Puerta Atrancada",
                image="app/cards/Puerta_atrancada.png",
            )
            Card(
                card_id = HACHA,
                name="Hacha",
                image="app/cards/Hacha.png",
            )
            flush()
    except:
        pass
