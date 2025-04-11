from collections.abc import Iterator
from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)
from sqlalchemy import Engine
from sqlmodel import (
    Session,
    create_engine,
)

DEFAULT_DB_DIALECT = "postgresql"
DEFAULT_DB_POOL_SIZE = 10
ROOT_DIR = Path(__file__).parent

class AlgorithmConfig(BaseSettings):
    api_host: str
    seed: str
    target_dispatches: int
    max_active_calls: int
    retry_count: int
    timeout: float

    model_config = SettingsConfigDict(
        env_prefix= "ALGORITHM_",
        env_file=ROOT_DIR / Path(".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_algorithm_config() -> AlgorithmConfig:
    return AlgorithmConfig()

DEFAULT_DB_DIALECT = "postgresql"
DEFAULT_DB_POOL_SIZE = 10

class DatabaseConfig(BaseSettings):
    host: str
    port: int
    username: str
    password: str
    database: str
    dialect: str = DEFAULT_DB_DIALECT
    pool_size: int = DEFAULT_DB_POOL_SIZE

    model_config = SettingsConfigDict(
        env_prefix= "DB_",
        env_file=ROOT_DIR / Path(".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

@lru_cache
def get_database_config() -> DatabaseConfig:
    return DatabaseConfig()

def get_connection_string() -> str:
    database_config = get_database_config()
    return (
        f"{database_config.dialect}://"
        f"{database_config.username}:{database_config.password}@"
        f"{database_config.host}:{database_config.port}/"
        f"{database_config.database}"
    )


def get_database_engine() -> Engine:
    database_config = get_database_config()
    return create_engine(get_connection_string(database_config), pool_size=database_config.pool_size)


def get_database_session() -> Iterator[Session]:
    engine = get_database_engine()
    with Session(engine) as session:
        yield session

if __name__ == "__main__":
    # algorithm_config = get_algorithm_config()

    # print(algorithm_config.api_host)

    print(get_connection_string())
