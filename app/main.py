from fastapi import FastAPI
from app.src.models.base import define_database_and_entities, load_cards
from app.src.router import card

define_database_and_entities()

load_cards()

app = FastAPI()

app.include_router(card.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

