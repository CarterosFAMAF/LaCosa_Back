from fastapi import WebSocket
from app.src.models.base import Player as PlayerDB
from pony.orm import *


class Player:
    _id : None

    def __init__(self, name):
        self.WebSocket: WebSocket = None

        with db_session:
            player_db = PlayerDB(name=name)
            flush()
            self._id = player_db.id
            