import json
import time
import logging
import logging.config

from clickhouse_driver.errors import Error
from kafka import KafkaConsumer
from kafka.errors import KafkaError

from modules.ch import ETLClickhouseDriver
from modules.kafka import ETLKafkaConsumer
from modules.transform import order_batches, transform
from settings.config import get_settings, log_conf
from settings.utils import backoff

logging.config.dictConfig(log_conf)
logger = logging.getLogger("main")

settings = get_settings()

@backoff
def connect_ch():
    return ETLClickhouseDriver(**settings.ch_settings.dict())


@backoff
def connect_kafka():
    return ETLKafkaConsumer(**settings.kafka_settings.dict()).get_consumer()


def run(
    kafka_consumer: KafkaConsumer, ch_driver: ETLClickhouseDriver, batch_size: int = 100
):
    batches_backup: list = []
    batches: list = []
    ch_driver.init_ch_database()
    while True:
        try:
            batches = batches_backup
            batches = []
            flush_start = time.time()
            while len(batches) < batch_size:
                for msg in kafka_consumer:
                    value = json.loads(msg.value)
                    batches.append(transform(value))
                    if len(batches) >= settings.app.flush_count or (time.time() - flush_start) >= settings.app.flush_seconds:
                        res = ch_driver.load(order_batches(batches))
                        # try next time
                        if not res:
                            continue

                        batches = []
                        flush_start = time.time()

        except KafkaError as kafka_error:
            logger.error("Got Kafka error: {0}".format(kafka_error))

        except Error as ch_error:
            logger.error("Got ClickHouse error: {0}".format(ch_error))
        finally:
            batches_backup = batches


if __name__ == "__main__":
    logger.info('Up\'n\'running')
    logger.debug('connect to Kafka')
    consumer = connect_kafka()
    logger.debug('connect to CH')
    ch_driver = connect_ch()
    logger.debug('databases ready to work!')
    run(consumer, ch_driver, batch_size=settings.app.batch_size)
