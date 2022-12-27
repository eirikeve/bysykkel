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

    app_name: str
    host: str
    port: int
    env: Literal["dev", "staging", "prod"]
    oslobysykkel_apiurl: AnyUrl

    class Config:
        env_prefix = "BYSYKKEL_"
