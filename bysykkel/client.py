from logging import getLogger
from typing import List
from urllib.parse import urlparse

from pydantic import parse_obj_as
from httpx import AsyncClient

from bysykkel.models import StationData, StationInfoResponse, StationStatusReponse


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
        """Query for info/metadata of the available city bike stations."""
        url: str = self.url("/station_information.json")
        self.logger.info(f"GET: {url}")
        response = await self.session.get(url)
        self.logger.debug(f"GET: {url} -> {response}")

        return parse_obj_as(StationInfoResponse, response.json())

    async def get_station_status(self) -> StationStatusReponse:
        """Query for the current status of the available city bike stations."""

        url = self.url("/station_status.json")
        self.logger.info(f"GET: {url}")
        response = await self.session.get(url)
        self.logger.debug(f"GET: {url} -> {response}")

        return parse_obj_as(StationStatusReponse, response.json())

    async def get_stations(self) -> List[StationData]:
        """Query for info/metadata and current status for the available city bike stations.

        The station info and station status are merged by id, so all data for each station is contained in one object.
        """

        status = await self.get_station_status()
        info = await self.get_station_information()

        status_by_id = {
            entry.station_id: entry.dict() for entry in status.data.stations
        }
        info_by_id = {entry.station_id: entry.dict() for entry in info.data.stations}

        stations_with_status = set(status_by_id)
        stations_with_info = set(info_by_id)
        stations_with_info_and_status = stations_with_info.intersection(
            stations_with_status
        )

        if stations_with_info != stations_with_status:
            missing_status = stations_with_info.difference(stations_with_status)
            missing_info = stations_with_status.difference(stations_with_info)
            if missing_info:
                self.logger.warning(
                    f"{len(missing_info)} stations have a status but no metadata: {missing_info}"
                )
            if missing_status:
                self.logger.warning(
                    f"{len(missing_status)} stations have metadata but no status: {missing_status}"
                )

        station_data = [
            {**info_by_id[station_id], **status_by_id[station_id]}
            for station_id in stations_with_info_and_status
        ]
        return parse_obj_as(List[StationData], station_data)
