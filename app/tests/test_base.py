from fastapi import status
from pony.orm import *
from fastapi.testclient import TestClient
from app.src.models.base import db
from app.main import app
from app.src.models.base import load_cards

client = TestClient(app=app)


@db_session
def test_load_cards():
    load_cards()
    assert db.exists("select * from Card where name = 'lanzallamas'")

