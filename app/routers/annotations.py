import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.annotation import AnnotationComment, AnnotationMixer
from app.models.session import Session
from app.schemas.annotation import AnnotationResponse, CommentRequest, MixerRequest
from app.services.auth import get_user_id_from_token

router = APIRouter(prefix="/session/annotate", tags=["annotations"])


async def _resolve_session(session_id: str, user_id: str, db: AsyncSession) -> Session:
    result = await db.execute(
        select(Session).where(
            Session.id == uuid.UUID(session_id),
            Session.user_id == uuid.UUID(user_id),
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session


@router.post("/comments", response_model=AnnotationResponse)
async def add_comment(body: CommentRequest, db: AsyncSession = Depends(get_db)):
    user_id = get_user_id_from_token(body.authtoken)
    await _resolve_session(body.sessionId, user_id, db)

    annotation = AnnotationComment(
        session_id=uuid.UUID(body.sessionId),
        timestamp=body.timestamp,
        comment=body.comment,
    )
    db.add(annotation)
    await db.commit()
    return AnnotationResponse()


@router.post("/mixer", response_model=AnnotationResponse)
async def add_mixer_event(body: MixerRequest, db: AsyncSession = Depends(get_db)):
    user_id = get_user_id_from_token(body.authtoken)
    await _resolve_session(body.sessionId, user_id, db)

    event = AnnotationMixer(
        session_id=uuid.UUID(body.sessionId),
        control=body.control,
        time_ms=body.time,
        value=body.value,
    )
    db.add(event)
    await db.commit()
    return AnnotationResponse()
