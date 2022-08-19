import backoff
from kafka import KafkaConsumer
from kafka.errors import KafkaError


class ETLKafkaConsumer:
    def __init__(self, host: list[str], topics: list[str], group_id: str):
        self.host = host
        self.topics = topics
        self.group_id = group_id

    @backoff.on_exception(backoff.expo, KafkaError)
    def get_consumer(self):
        return KafkaConsumer(
            *self.topics, bootstrap_servers=self.host, group_id=self.group_id
        )
