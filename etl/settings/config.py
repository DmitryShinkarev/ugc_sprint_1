import yaml
from pathlib import Path

from functools import lru_cache

from pydantic import BaseSettings, Field

# инициализируем конфиг для logging
path_log_conf = Path(__file__).parent.joinpath("log_conf.yaml")
with path_log_conf.open("r") as f:
    log_conf = yaml.safe_load(f)


class AppSettings(BaseSettings):
    host: str = Field("localhost", env="APP_HOST")
    port: int = Field(5000, env="APP_PORT")
    batch_size: int = Field(100, env="BATCH_SIZE")
    flush_seconds: int = Field(30, env="FLUSH_SECONDS")
    flush_count: int = Field(1000, env="FLUSH_COUNT")


class KafkaSettings(BaseSettings):
    host: list[str] = Field(["localhost:29092"], env="KAFKA_HOST")
    topics: list[str] = Field(["movie_topic"], env="EVENT_TYPES")
    group_id: str = Field("", env="KAFKA_GROUP_ID")


class ClickHouseSettings(BaseSettings):
    host: str = Field("localhost:9000", env="CH_HOST")
    db: str = Field("movies", env="CH_DB")
    tables: list[str] = Field(["movie_topic"], env="EVENT_TYPES")


class Settings(BaseSettings):
    app = AppSettings()
    kafka_settings = KafkaSettings()
    ch_settings = ClickHouseSettings()


@lru_cache
def get_settings() -> Settings:
    return Settings()
