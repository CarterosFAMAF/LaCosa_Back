from pony.orm import *
from app.src.game.constants import *
import random

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


# imagenes para infeccion


@db_session
def load_cards():
    image_infected = [
        "app/cards/Infeccion_1.png",
        "app/cards/Infeccion_2.png",
        "app/cards/Infeccion_3.png",
    ]
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
                card_id=MAS_VALE_QUE_CORRAS,
                name="Mas_Vale_Que_Corras",
                image="app/cards/Mas_vale_que_corras.png",
            )
            Card(
                card_id=SOSPECHA,
                name="Sospecha",
                image="app/cards/sospecha.png",
            )
            Card(
                card_id=VIGILA_TUS_ESPALDAS,
                name="Vigila_Tus_Espaldas",
                image="app/cards/Vigila_tus_espaldas.png",
            )
            Card(
                card_id=WHISKY,
                name="Whisky",
                image="app/cards/Whisky.png",
            )
            Card(
                card_id=ANALISIS,
                name="Analisis",
                image="app/cards/Analisis.png",
            )
            Card(
                card_id=CAMBIO_DE_LUGAR,
                name="Cambio_de_lugar",
                image="app/cards/Cambio_de_lugar.png",
            )
            Card(
                card_id=SEDUCCION,
                name="Seduccion",
                image="app/cards/Seduccion.png",
            )
            Card(
                card_id=UPS,
                name="Ups!",
                image="app/cards/Ups!.png",
            )
            Card(
                card_id=CITA_A_CIEGAS,
                name="Cita_a_ciegas",
                image="app/cards/Cita_a_ciegas.png",
            )
            Card(
                card_id=QUE_QUEDE_ENTRE_NOSOTROS,
                name="Que_quede_entre_nosotros",
                image="app/cards/Que_quede_entre_nosotros.png",
            )
            Card(
                card_id=INFECCION,
                name="Infeccion",
                image=random.choice(image_infected),
            )
            flush()
    except:
        pass
