from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from app.constants import origins
from app.src.models.base import define_database_and_entities
from app.src.router import match_router


define_database_and_entities()


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
