from logging import getLogger
from urllib.parse import urlparse

from pydantic import parse_obj_as
from httpx import AsyncClient

from bysykkel.models import StationInfoResponse, StationStatusReponse


class BysykkelClient:
    """Client class for reading from Oslo Bysykkel's real time API.

    NOTE: Oslo Bysykkel provides a GBFS auto discovery schema,
          which could be used to resolve URLs to other endpoints.
          That'd enable supporting other GBFS data providers with the same client.

    Reference:
        Oslo Bysykkel: https://oslobysykkel.no/apne-data/sanntid
    """

    def __init__(self, base_url: str) -> None:
        self.base_url = urlparse(base_url)
        self.session = AsyncClient(headers={"Client-Identifier": "eirikeve-bysykkel"})
        self.logger = getLogger(type(self).__name__)
        self.logger.info(f"Initialized with base_url {base_url}")

    def url(self, endpoint: str) -> str:
        endpoint = endpoint.removeprefix("/")
        full_path = f"{self.base_url.path}/{endpoint}"
        return self.base_url._replace(path=full_path).geturl()

    async def get_station_information(self) -> StationInfoResponse:
        url: str = self.url("/station_information.json")
        response = await self.session.get(url)
        return parse_obj_as(StationInfoResponse, response.json())

    async def get_station_status(self) -> StationStatusReponse:
        url = self.url("/station_status.json")
        response = await self.session.get(url)
        return parse_obj_as(StationStatusReponse, response.json())
