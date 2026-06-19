import uuid

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.recording import Recording
from app.models.session import Session, SessionStatus
from app.schemas.recording import RecordingUploadResponse
from app.services.auth import get_user_id_from_token
from app.services.s3 import upload_file
from app.services.storage import build_s3_key, content_type_for, resolve_file_type

router = APIRouter(prefix="/recording", tags=["recordings"])


@router.post("/upload", response_model=RecordingUploadResponse)
async def upload_recording(
    authtoken: str = Form(...),
    sessionId: str = Form(...),
    file: UploadFile = ...,
    db: AsyncSession = Depends(get_db),
):
    user_id = get_user_id_from_token(authtoken)

    result = await db.execute(
        select(Session).where(
            Session.id == uuid.UUID(sessionId),
            Session.user_id == uuid.UUID(user_id),
            Session.status == SessionStatus.active,
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active session not found",
        )

    filename = file.filename or f"upload_{uuid.uuid4()}.bin"
    file_type = resolve_file_type(filename)
    s3_key = build_s3_key(user_id, sessionId, filename)
    file_bytes = await file.read()

    size = await upload_file(file_bytes, s3_key, content_type_for(filename))

    recording = Recording(
        session_id=uuid.UUID(sessionId),
        file_type=file_type,
        original_filename=filename,
        s3_key=s3_key,
        file_size_bytes=size,
    )
    db.add(recording)
    await db.commit()

    return RecordingUploadResponse(s3_key=s3_key, file_size_bytes=size)
