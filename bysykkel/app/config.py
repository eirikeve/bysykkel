from typing import Literal

from fastapi import FastAPI
from pydantic import BaseSettings, AnyUrl


class Settings(BaseSettings):
    """Settings for Bysykkel REST API

    Field values are loaded from environment variables with a `bysykkel_` prefix upon instantiation.
    E.g., `BYSYKKEL_APP_NAME=foobar` is loaded into `Settings.app_name`.
    See the `.env` at the repo root for a configuration example.

    References:
        Pydantic BaseSettings: https://docs.pydantic.dev/usage/settings/
    """

    app_name: str = "App"
    host: str = "127.0.0.1"
    port: int = 8000
    env: Literal["dev", "staging", "prod"] = "dev"
    oslobysykkel_apiurl: AnyUrl = "https://gbfs.urbansharing.com/oslobysykkel.no"  # type: ignore

    class Config:
        env_prefix = "BYSYKKEL_"
