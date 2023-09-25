from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.src.models.base import define_database_and_entities, load_cards
from app.src.router import match_router
from app.src.router import card

define_database_and_entities()

load_cards()


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]


app = FastAPI()

app.include_router(card.router)
app.include_router(match_router.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

