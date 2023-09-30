from fastapi import WebSocket
from app.src.models.base import Player as PlayerDB
from pony.orm import *


class Player:
    def __init__(self, name):
        self._name = name
        self._position = None
        self._role = None
        self._match = None
        self._cards = None
        self._websocket = None
