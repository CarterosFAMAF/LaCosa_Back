class Carta:
    def __init__(self, nombre, cant_de_jugadores, tipo, descripcion):
        self.nombre = nombre
        self.cant_de_jugadores = cant_de_jugadores
        self.tipo = tipo
        self.descripcion = descripcion

    def __str__(self):
        return self.nombre