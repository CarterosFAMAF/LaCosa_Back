from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.constants import origins
from app.src.models.base import define_database_and_entities, load_cards
from app.src.router import match_router


define_database_and_entities(test=True)

load_cards()

test_app = FastAPI()


test_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

test_app.include_router(match_router.router)
