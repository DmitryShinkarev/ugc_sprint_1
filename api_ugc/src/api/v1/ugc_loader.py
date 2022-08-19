import logging
from http import HTTPStatus
from uuid import UUID

from aiokafka import AIOKafkaProducer
from fastapi import APIRouter, Depends, HTTPException, Query
from models.event import EventForUGS
from storage.kafka import get_aioproducer

from core.settings import get_settings
from services.ugc_kafka_producer import ugc_kafka_producer

router = APIRouter()
logger = logging.getLogger(__name__)


def create_answer(*, was_loaded: bool, movie_id: UUID, user_id: UUID) -> dict:
    return {
        "result": {
            "was_loaded": was_loaded,
            "movie_id": str(movie_id),
            "user_id": str(user_id),
        }
    }


@router.post("/produce", summary="UGC produce endpoint", status_code=HTTPStatus.CREATED)
async def inner_produce(
    event_for_ugs: EventForUGS, producer: AIOKafkaProducer = Depends(get_aioproducer)
):
    """Endpoint write message single event to Kafka"""
    logger.debug(event_for_ugs)

    was_produced: bool = await ugc_kafka_producer.produce(
        request_for_ugs=event_for_ugs, producer=producer
    )
    result = create_answer(
        was_loaded=was_produced,
        movie_id=event_for_ugs.payload.movie_id,
        user_id=event_for_ugs.payload.user_id,
    )
    if not was_produced:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=result)
    return result


@router.post(
    "/batch_produce",
    summary="UGC batch produce endpoint",
    status_code=HTTPStatus.CREATED,
)
async def batch_inner(
    events_for_ugs: list[EventForUGS],
    producer: AIOKafkaProducer = Depends(get_aioproducer),
):
    """Endpoint write list to Kafka"""
    logger.debug(events_for_ugs)
    was_produced: bool = await ugc_kafka_producer.batch_produce(
        requests=events_for_ugs, producer=producer
    )
    result = {"batch_produced": was_produced}
    if not was_produced:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=result)
    return result


if get_settings().app.is_debug:
    from models.event import create_random_event

    # WARNING only for debug
    @router.post(
        "/random_batch_produce",
        summary="Debug UGC batch produce endpoint",
        status_code=HTTPStatus.CREATED,
    )
    async def random_batch_produce(
        batch_count: int = Query(default=500, alias="batch_count"),
        producer: AIOKafkaProducer = Depends(get_aioproducer),
    ):
        """Endpoint make {batch_count} valid message service"""
        batch = [create_random_event() for _ in range(batch_count)]
        were_produced: bool = await ugc_kafka_producer.batch_produce(
            requests=batch, producer=producer
        )
        result = {"batch_produced": were_produced}
        if not were_produced:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=result)
        return result
