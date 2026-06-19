from pydantic import BaseModel


class RecordingUploadResponse(BaseModel):
    status: str = "success"
    s3_key: str
    file_size_bytes: int
