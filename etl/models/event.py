from typing import Optional
from uuid import UUID

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class BaseETLModel(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Payload(BaseETLModel):
    movie_id: UUID
    user_id: UUID
    event_data: Optional[str]
    event_timestamp: int

    def dict(self, *args, **kwargs):
        result: dict = super().dict(*args, **kwargs)
        result["movie_id"] = str(result["movie_id"])
        result["user_id"] = str(result["user_id"])
        return result


class EventForUGS(BaseETLModel):
    payload: Payload
    language: Optional[str]
    timezone: Optional[str]
    ip: Optional[str]
    version: Optional[str]
    client_data: Optional[str]
    event_type: str
