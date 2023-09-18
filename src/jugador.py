class Jugador:
    def __init__(self, id, nombre, posicion, rol, partida, cartas):
        self.id = id
        self.nombre = nombre
        self.posicion = posicion
        self.rol = rol
        self.partida = partida
        self.cartas = cartas
        
        def __str__(self):
            return f'Jugador({self.id}, {self.nombre}, {self.posicion}, {self.rol}, {self.partida}, {self.cartas})'
        