from fastapi import WebSocket
from match import Match

class Player:
    id = None               #Por ahora podria asignar el id por orden de entrada.
    name : str
    position : int
    role : str
    match : Match
    card : list[Card]
    websocket : WebSocket

    def __init__(self, name):
        self.id = None
        self.name = name
        self.position = None
        self.role = None
        self.match = None
        self.cards : list[card] = []
        self.websocket = None

    def play_card(self,player_out:Player,match : Match,card):
        apply_effect(self,player_out,match)         #aplica el efecto de carta
        delete_card(self,card)                      #busca card y lo elimina del mazo de cartas del usuario
        match.discard_pile.append(card)             #pone la carta utilizada en la pila de descartes
