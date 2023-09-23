from fastapi import WebSocket


class Player:
    def __init__(self, name):
        self.id = None
        self.name = name
        self.position = None
        self.role = None
        self.match = None
        self.cards = None
        self.websocket = None
