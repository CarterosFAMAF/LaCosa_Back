from fastapi import APIRouter, status, HTTPException

from app.src.game.match import Match

from app.src.router.schemas import MatchIn, MatchOut

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
