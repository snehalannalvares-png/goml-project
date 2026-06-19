from pydantic import BaseModel


class SessionStartRequest(BaseModel):
    authtoken: str


class SessionStartResponse(BaseModel):
    sessionId: str


class SessionEndRequest(BaseModel):
    authtoken: str
    sessionId: str


class SessionEndResponse(BaseModel):
    status: str = "success"
