import logging

import backoff
from clickhouse_driver import Client
from clickhouse_driver.errors import Error


class ETLClickhouseDriver:
    def __init__(self, host: str, db: str, tables: list[str]):
        self.host = host
        self.db = db
        self.tables = tables
        self.client = self.get_ch_client()

    @backoff.on_exception(backoff.expo, Error)
    def get_ch_client(self):
        return Client.from_url(self.host)

    def init_ch_database(self):
        self.client.execute(
            f"CREATE DATABASE IF NOT EXISTS {self.db} ON CLUSTER ya_middle_prk"
        )
        for table in self.tables:
            self.client.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.db}.{table} ON CLUSTER ya_middle_prk
                    (
                        language String,
                        timezone String,
                        ip String,
                        version String,
                        movie_id UUID,
                        user_id UUID,
                        event_data String,
                        event_timestamp String
                    )
                    Engine=MergeTree()
                ORDER BY event_timestamp
                """
            )

    def load(self, data: dict):
        for event_type, batch in data.items():
            try:
                self.client.execute(
                    f"INSERT INTO {self.db}.{event_type} VALUES",
                    batch,
                    types_check=True,
                )
                return True
            except KeyError as ch_err:
                logging.error(
                    "Error while loading data into Clickhouse: {0}".format(ch_err)
                )
