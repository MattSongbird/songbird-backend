from app.utils.token_tracker import get_token_usage

from fastapi import APIRouter, Query


router = APIRouter()

@router.get("/metrics/tokens")
def token_metrics(session_id: str = Query(...)) -> None:
    return {
        "session_id": session_id,
        "usage": get_token_usage(session_id)
    }
