from fastapi import *
from pony.orm import *
from app.src.models.base import *

router = APIRouter()

@router.get("/carta")
@db_session
def get_carta():
    card = None
    cname = "lanzallamas"
    msg = {}
    card_exist =db.exists("select * from Card where name=$cname")
    if card_exist:
        card = db.get("select * from Card where name=$cname")
        msg = {"cardtype": card.type}
    else:
        msg = {"cardtype": card_exist}
    return msg