from fastapi import WebSocket
from jugador import Jugador

PARTIDAS = []


class Partida:
    def __init__(
        self, nombre_jugador, nombre_partida, nro_max_jugadores, nro_min_jugadores
    ):
        self.id = len(PARTIDAS)
        self.nombre = nombre_partida
        self.nro_max_jugadores = nro_max_jugadores
        self.nro_min_jugadores = nro_min_jugadores
        self.dueño = Jugador(nombre_jugador)
        self.empezada = False
        self.finalizada = False
        self.turno = None
        self.jugadores = None
        self.cartas_maso = None
        self.cartas_descarte = None

        PARTIDAS.append(self)
        print(PARTIDAS)

    def agregar_jugador(self, jugador):
        self.jugadores.append(jugador)

    def sacar_jugador(self, jugador):
        self.jugadores.remove(jugador)

    def agregar_carta_maso(self, carta):
        self.cartas_maso.append(carta)

    def sacar_carta_maso(self, carta):
        self.cartas_maso.remove(carta)

    def agregar_carta_descarte(self, carta):
        self.cartas_descarte.append(carta)

    def sacar_carta_descarte(self, carta):
        self.cartas_descarte.remove(carta)

    def empezar_partida(self):
        self.empezada = True

    def finalizar_partida(self):
        self.finalizada = True
        self.empezada = False

    def siguiente_turno(self):
        self.turno = (self.turno + 1) % len(self.jugadores)

    def __str__(self):
        return self.nombre
