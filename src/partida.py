class Partida:
    def __init__(self, nombre, nro_jugadores, nro_min_jugadores):
        self.nombre = nombre
        self.nro_jugadores = nro_jugadores
        self.nro_min_jugadores = nro_min_jugadores
        self.empezada = False
        self.finalizada = False
        self.turno = 0
        self.jugadores = []
        self.cartas_maso = []
        self.cartas_descarte = []

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

    def siguiente_turno(self):
        self.turno = (self.turno + 1) % len(self.jugadores)

    def __str__(self):
        return self.nombre