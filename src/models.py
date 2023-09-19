from pony.orm import *


db = Database()


class Partida(db.Entity):
    id = PrimaryKey(int, auto=True)
    nombre = Required(str)
    nro_jugadores = Required(int)
    empezada = Required(bool)
    finalizada = Required(bool)
    turno = Required(int)
    nro_min_jugadores = Required(int)
    jugadores = Set("Jugador")
    cartas_maso = Set("Carta", reverse="partida")
    cartas_descarte = Set("Carta", reverse="partida_descarte")


class Carta(db.Entity):
    nombre = Required(str)
    cant_de_jugadores = Required(int)
    tipo = Required(str)
    descripcion = Required(str)
    jugador = Required("Jugador")
    partida = Required(Partida, reverse="cartas_maso")
    partida_descarte = Required(Partida, reverse="cartas_descarte")


class Jugador(db.Entity):
    id = PrimaryKey(int, auto=True)
    nombre = Required(str)
    posicion = Required(int)
    rol = Required(str)
    partida = Required(Partida)
    cartas = Set(Carta)


# Conecta a la base de datos SQLite en el archivo 'database.sqlite'
db.bind(provider="sqlite", filename="database.sqlite", create_db=True)

# Genera las tablas en la base de datos
db.generate_mapping(create_tables=True)
