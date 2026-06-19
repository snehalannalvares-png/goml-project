import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.session import Session, SessionStatus
from app.schemas.session import (
    SessionEndRequest,
    SessionEndResponse,
    SessionStartRequest,
    SessionStartResponse,
)
from app.services.auth import get_user_id_from_token
from app.services.storage import build_s3_prefix

router = APIRouter(prefix="/session", tags=["sessions"])


@router.post("/start", response_model=SessionStartResponse)
async def session_start(body: SessionStartRequest, db: AsyncSession = Depends(get_db)):
    user_id = get_user_id_from_token(body.authtoken)
    session_id = uuid.uuid4()
    s3_prefix = build_s3_prefix(user_id, str(session_id))

    session = Session(
        id=session_id,
        user_id=uuid.UUID(user_id),
        s3_prefix=s3_prefix,
    )
    db.add(session)
    await db.commit()

    return SessionStartResponse(sessionId=str(session_id))


@router.post("/end", response_model=SessionEndResponse)
async def session_end(body: SessionEndRequest, db: AsyncSession = Depends(get_db)):
    user_id = get_user_id_from_token(body.authtoken)

    result = await db.execute(
        select(Session).where(
            Session.id == uuid.UUID(body.sessionId),
            Session.user_id == uuid.UUID(user_id),
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    if session.status == SessionStatus.completed:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Session already ended")

    session.status = SessionStatus.completed
    session.ended_at = datetime.now(timezone.utc)
    await db.commit()

    return SessionEndResponse()
