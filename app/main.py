from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.constants import origins
from app.src.models.base import define_database_and_entities, load_cards
from app.src.router import match_router

print ("ANTES DE DATABASE AND ENTITIES")
define_database_and_entities(test=False)
print ("ANTES DEE LOAD CARDS")
load_cards()
print ("DESPUES DE LOAD CARDS")
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(match_router.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
