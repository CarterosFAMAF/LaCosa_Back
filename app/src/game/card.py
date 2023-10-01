from app.src.models.base import Match as MatchDB
from app.src.models.base import Player as PlayerDB
from pony.orm import *

class Card:
    id : None
    name: str

    def __init__(self,name):
        self.name = name


    def lanzallamas(player_out_id,match_id):
        with db_session:
            player_db = PlayerDB.get(id = player_out_id)
            player_db.alive = False
            flush()
            match = MatchDB.get(id = match_id)
            match.player_alive -= 1
            flush()
        return {"player": player_db.id, "status": "is dead"}
