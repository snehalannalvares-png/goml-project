from pydantic import BaseModel


class CommentRequest(BaseModel):
    authtoken: str
    sessionId: str
    timestamp: str
    comment: str


class MixerRequest(BaseModel):
    authtoken: str
    sessionId: str
    control: str
    time: int
    value: str


class AnnotationResponse(BaseModel):
    status: str = "success"
