from fastapi import APIRouter, status, HTTPException, WebSocket, WebSocketDisconnect
from app.src.game.match import Match, MATCHS
from app.src.game.player import Player
from app.src.router.schemas import MatchIn, MatchOut
from src.models.models import *

router = APIRouter()


@router.post("/matchs", response_model=MatchOut, status_code=status.HTTP_201_CREATED)
async def create_match(match: MatchIn):
    try:
        new_match = Match(
            match.player_name,
            match.match_name,
            match.max_players,
            match.min_players,
        )
    except ValueError as e:
        raise HTTPException(
            {
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "detail": str(e),
            }
        )
    return MatchOut(
        match_id=new_match.id,
        match_name=new_match.name,
        owner_id=new_match.owner.id,
        result="Match created",
    )


# websocket endpoint
@router.websocket("/ws/matchs/{match_id}/{player_id}")                              #--> Que es un websocet endpoint ?
async def websocket_endpoint(websocket: WebSocket, match_id: int, player_id: int):
    # seteo variables para usar aca
    match = MATCHS[match_id]
    player = match.players[player_id]
    manager = match.match_connection_manager

    # seteo websocket en el objeto jugador para a futuro poder mandarle algo privado
    player.websocket = websocket

    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{player.name} says: {data}")
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        await manager.broadcast(f"Client #{player.name} left the chat")

@router.post("/partidas/{match_id}/{player_name}/jugadores")
def join_match_endpoint(match_id: Match , player_name : str):
    
    new_player = Player(new_player,player_name)     #deberia crear un modelo.
    Match.add_player(match_id,new_player)

    msg = {"msg" : "Se creo el jugador con éxito!", "Player id" : new_player.id}
    return msg

    #deberia unir al websocket , actualizar los datos de la partida, devolver el id de la partida.