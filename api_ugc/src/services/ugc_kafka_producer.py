import json
import logging
from random import choice
from uuid import uuid4

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError
from models.event import EventForUGS

from core.settings import get_settings

logger = logging.getLogger(__name__)


class UGCKafkaProducer:
    @staticmethod
    def serializer(value):
        return json.dumps(value).encode()

    def __init__(self) -> None:
        self.hosts = ",".join(get_settings().kafka_settings.hosts)
        self.topics = get_settings().kafka_settings.topics

    def _get_key(self) -> str:
        return str(uuid4()).encode()

    async def produce(self, request_for_ugs: EventForUGS, producer: AIOKafkaProducer):
        was_produced = False
        if request_for_ugs.event_type not in self.topics:
            return was_produced
        try:
            key = self._get_key()
            await producer.send(
                topic=request_for_ugs.event_type, value=request_for_ugs.dict(), key=key
            )
            was_produced = True
            logger.info("Message sent with uuid=%s", key.decode())
        except KafkaError as kafka_error:
            logger.exception(kafka_error)
        return was_produced

    async def send_batch(self, producer, batch, topic: str):
        partitions = await producer.partitions_for(topic)
        partition = choice(tuple(partitions))
        await producer.send_batch(batch, topic=topic, partition=partition)
        logger.info(
            "%d messages sent to partition %d of %s topic"
            % (batch.record_count(), partition, topic)
        )

    def _parse_batch_by_event_type(
        self, requests: list[EventForUGS]
    ) -> dict[str, dict]:
        result_batch = {}
        for request in requests:
            if (
                request.event_type not in result_batch
                and request.event_type in self.topics
            ):
                result_batch[request.event_type] = []
            result_batch[request.event_type].append(request.dict())
        return result_batch

    async def batch_produce(
        self, requests: list[EventForUGS], producer: AIOKafkaProducer
    ):
        were_produced = []
        parsed_batch = self._parse_batch_by_event_type(requests=requests)
        for topic, topic_batch in parsed_batch.items():
            try:
                batch = producer.create_batch()
                submission = 0
                while submission < len(topic_batch):
                    metadata = batch.append(
                        key=self._get_key(),
                        value=UGCKafkaProducer.serializer(topic_batch[submission]),
                        timestamp=None,
                    )
                    if metadata is None:
                        await self.send_batch(
                            producer=producer, batch=batch, topic=topic
                        )
                        batch = producer.create_batch()
                        continue
                    submission += 1
                await self.send_batch(producer=producer, batch=batch, topic=topic)
                were_produced.append(True)
            except KafkaError as kafka_error:
                logger.exception(kafka_error)
                were_produced.append(False)
        return all(were_produced)


ugc_kafka_producer = UGCKafkaProducer()
