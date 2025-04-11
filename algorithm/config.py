from collections.abc import Iterator
from functools import lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import Depends
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

    model_config = SettingsConfigDict(
        env_prefix= "ALGORITHM_",
        env_file=ROOT_DIR / Path(".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_algorithm_config() -> AlgorithmConfig:
    return AlgorithmConfig()

algorithm_config = get_algorithm_config()

print(algorithm_config.api_host)

# def get_connection_string(database_config: Annotated[DatabaseConfig, Depends(get_database_config)]) -> str:
#     return (
#         f"{database_config.dialect}://"
#         f"{database_config.username}:{database_config.password}@"
#         f"{database_config.host}:{database_config.port}/"
#         f"{database_config.database}"
#     )


# def get_database_engine(database_config: Annotated[DatabaseConfig, Depends(get_database_config)]) -> Engine:
#     return create_engine(get_connection_string(database_config), pool_size=database_config.pool_size)


# def get_database_session(engine: Annotated[Engine, Depends(get_database_engine)]) -> Iterator[Session]:
#     with Session(engine) as session:
#         yield session
