from pydantic import BaseModel


class Message(BaseModel):
    detail: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
