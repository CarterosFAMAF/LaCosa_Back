from pony.orm import *
from app.src.game.constants import *
import random

db = Database()


class Message(db.Entity):
    id = PrimaryKey(int, auto=True)
    message = Required(str)
    match = Optional("Match", reverse="messages")
    player = Optional("Player", reverse="messages")


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
    messages = Set("Message", reverse="match")


class Player(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    position = Optional(int, default=-1)
    role = Optional(str)
    hand = Set("Card")
    match = Optional(Match, reverse="players")
    match_owner = Optional(Match, reverse="player_owner")
    card_exchange = Optional("Card", reverse="player_card_exchange")
    messages = Set("Message", reverse="player")


class Card(db.Entity):
    """
    Tabla donde guardar las cartas
    """

    id = PrimaryKey(int, auto=True)
    card_id = Required(int)
    name = Required(str)
    image = Required(str)
    type = Required(str)
    player_hand = Set(Player)
    deck = Set(Match, reverse="deck")
    discard_deck = Set(Match, reverse="discard_pile")
    player_card_exchange = Optional(Player, reverse="card_exchange")


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
            # LA COSA
            Card(
                card_id=LA_COSA,
                name="La_Cosa",
                image="app/cards/La_Cosa.png",
                type=TYPE_LA_COSA,
            )
            # CARTAS ACCION
            Card(
                card_id=LANZALLAMAS,
                name="Lanzallamas",
                image="app/cards/Lanzallamas.png",
                type=TYPE_ACTION,
            )
            Card(
                card_id=MAS_VALE_QUE_CORRAS,
                name="Mas_vale_que_corras",
                image="app/cards/Mas_vale_que_corras.png",
                type=TYPE_ACTION,
            )
            Card(
                card_id=SOSPECHA,
                name="Sospecha",
                image="app/cards/Sospecha.png",
                type=TYPE_ACTION,
            )
            Card(
                card_id=VIGILA_TUS_ESPALDAS,
                name="Vigila_tus_espaldas",
                image="app/cards/Vigila_tus_espaldas.png",
                type=TYPE_ACTION,
            )
            Card(
                card_id=WHISKY,
                name="Whisky",
                image="app/cards/Whisky.png",
                type=TYPE_ACTION,
            )
            Card(
                card_id=ANALISIS,
                name="Analisis",
                image="app/cards/Analisis.png",
                type=TYPE_ACTION,
            )
            Card(
                card_id=CAMBIO_DE_LUGAR,
                name="Cambio_de_lugar",
                image="app/cards/Cambio_de_lugar.png",
                type=TYPE_ACTION,
            )
            Card(
                card_id=SEDUCCION,
                name="Seduccion",
                image="app/cards/Seduccion.png",
                type=TYPE_ACTION,
            )
            # CARTAS DEFENSA
            Card(
                card_id=AQUI_ESTOY_BIEN,
                name="Aqui_Estoy_Bien",
                image="app/cards/Aqui_estoy_bien.png",
                type=TYPE_DEFENSE,
            )
            Card(
                card_id=FALLASTE,
                name="Fallaste",
                image="app/cards/Fallaste.png",
                type=TYPE_DEFENSE,
            )
            Card(
                card_id=ATERRADOR,
                name="Aterrador",
                image="app/cards/Aterrador.png",
                type=TYPE_DEFENSE,
            )
            Card(
                card_id=NO_GRACIAS,
                name="No_gracias",
                image="app/cards/No_gracias.png",
                type=TYPE_DEFENSE,
            )
            Card(
                card_id=NADA_DE_BARBACOAS,
                name="Nada_de_barbacoas",
                image="app/cards/Nada_de_barbacoas.png",
                type=TYPE_DEFENSE,
            )
            Card(
                card_id=INFECCION,
                name="Infeccion",
                image=random.choice(image_infected),
                type=TYPE_INFECTED,
            )
            flush()
    except:
        pass
