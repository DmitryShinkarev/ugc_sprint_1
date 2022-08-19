from typing import Optional

from aiokafka import AIOKafkaProducer

aioproducer: Optional[AIOKafkaProducer] = None


async def get_aioproducer() -> aioproducer:
    return aioproducer
