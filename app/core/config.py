import warnings
from typing import Annotated, Any, Literal

from pydantic import BeforeValidator, PostgresDsn, computed_field, model_validator
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


def parse_array(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/v1"
    API_KEY: str | None = None
    # 60 minutes * 24 hours * 8 days = 8 days
    ENVIRONMENT: Literal["dev", "production"] = "dev"

    POSTGRES_SERVER: str | None = None
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    SQLITE_PATH: str | None = None

    DATABASE_POOL_SIZE: int = 20
    DATABASE_POOL_MAX_OVERFLOW: int = 10

    DEFAULT_LOGBOOKS: Annotated[list[str] | str, BeforeValidator(parse_array)] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def POSTGRES_DATABASE_URI(self) -> PostgresDsn | None:
        return (
            MultiHostUrl.build(
                scheme="postgresql+psycopg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
            if self.POSTGRES_SERVER
            else None
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLITE_DATABASE_URI(self) -> str | None:
        return f"sqlite://{self.SQLITE_PATH}" if self.SQLITE_PATH else None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str | None:
        if self.POSTGRES_DATABASE_URI and self.SQLITE_DATABASE_URI:
            raise ValueError("Only one database can be set at a time")
        
        if self.POSTGRES_DATABASE_URI:
            return str(self.POSTGRES_DATABASE_URI)
        
        if self.SQLITE_DATABASE_URI:
            return self.SQLITE_DATABASE_URI

        raise ValueError("No database set")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_ARGS(self) -> dict:
        if self.POSTGRES_DATABASE_URI and self.SQLITE_DATABASE_URI:
            raise ValueError("Only one database can be set at a time")
        
        if self.POSTGRES_DATABASE_URI:
            return {
                "pool_size": self.DATABASE_POOL_SIZE,
                "max_overflow": self.DATABASE_POOL_MAX_OVERFLOW
            }
        
        if self.SQLITE_DATABASE_URI:
            return {}

        raise ValueError("No database set")

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "dev":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("API_KEY", self.API_KEY)
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)

        return self

    @model_validator(mode="after")
    def _auth_check(self) -> Self:
        if self.API_KEY is None:
            message = "API_KEY is not set, API will be open to the public."
            if self.ENVIRONMENT == "dev":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

        return self


settings = Settings()  # type: ignore
