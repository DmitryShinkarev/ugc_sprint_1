from functools import lru_cache

from pydantic import BaseSettings, Field


class AppSettings(BaseSettings):
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")
    is_debug: bool = Field(True, env="DEBUG")
    should_reload: bool = Field(True, env="SHOULD_RELOAD")

    should_check_jwt: bool = Field(False, env="SHOULD_CHECK_JWT")
    jwt_public_key = Field("JWT_PUBLIC_KEY", env="JWT_PUBLIC_KEY")
    jwt_algorithm = Field("HS256", env="JWT_ALGORITHM")


class KafkaSettings(BaseSettings):
    kafka_bootstrap_servers: list = ['broker:29092']
    algorithm: str = 'HS256'
    hosts: list[str] = Field(["127.0.0.1:29092"], env="KAFKA_HOSTS")
    topics: list[str] = Field(
        [
            "movie_like",
            "movie_dislike",
            "movie_share",
            "movie_comment",
        ],
        env="KAFKA_TOPIC",
    )
    project_name: str = Field("movie_kafka_producer", env="PROJECT_NAME")


class RedisSettings(BaseSettings):
    endpoint: str = Field("127.0.0.1", env="REDIS_HOST")
    port: int = Field(6379, env="REDIS_PORT")


class Settings(BaseSettings):
    app = AppSettings()
    kafka_settings = KafkaSettings()
    redis_settings = RedisSettings()


@lru_cache
def get_settings() -> Settings:
    return Settings()
