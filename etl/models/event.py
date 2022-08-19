from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class Payload(BaseModel):
    movie_id: UUID
    user_id: UUID
    event_data: Optional[str]
    event_timestamp: int

    def dict(self, *args, **kwargs):
        result: dict = super().dict(*args, **kwargs)
        result["movie_id"] = str(result["movie_id"])
        result["user_id"] = str(result["user_id"])
        return result


class EventForUGS(BaseModel):
    payload: Payload
    language: Optional[str]
    timezone: Optional[str]
    ip: Optional[str]
    version: Optional[str]
    client_data: Optional[str]
    event_type: str
