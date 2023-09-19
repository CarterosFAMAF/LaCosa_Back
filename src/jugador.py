from fastapi import WebSocket

JUGADORES = []


class Jugador:
    def __init__(self, nombre):
        self.id = len(JUGADORES)
        self.nombre = nombre
        self.posicion = None
        self.rol = None
        self.partida = None
        self.cartas = None
        self.websocket = None
