from datetime import datetime
from random import choice, randint
from typing import Optional
from uuid import UUID, uuid4

import orjson
from core.settings import get_settings
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class BaseUGCModel(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Payload(BaseUGCModel):
    movie_id: UUID
    user_id: UUID
    event_data: Optional[str]
    event_timestamp: int

    def dict(self, *args, **kwargs):
        result: dict = super().dict(*args, **kwargs)

        result["movie_id"] = str(result["movie_id"])
        result["user_id"] = str(result["user_id"])
        return result


class EventForUGS(BaseUGCModel):
    payload: Payload
    event_type: str
    language: Optional[str]
    timezone: Optional[str]
    ip: Optional[str]
    version: Optional[str]
    client_data: Optional[str]

    def dict(self, *args, **kwargs):
        result: dict = super().dict(*args, **kwargs)

        del result["event_type"]
        return result


if get_settings().app.is_debug:

    def create_random_event() -> EventForUGS:
        request: EventForUGS = EventForUGS(
            language=choice(("ru", "en", "fr")),
            timezone=f"gmt+{randint(0,12)}",
            ip=f"{randint(0,254)}.{randint(0,254)}.{randint(0,254)}.{randint(0,254)}",
            version="1.0",
            event_type=choice(get_settings().kafka_settings.topics),
            payload=Payload(
                movie_id=uuid4(),
                user_id=uuid4(),
                event_data="event_data",
                event_timestamp=int(datetime.now().timestamp()),
            ),
        )
        return request
