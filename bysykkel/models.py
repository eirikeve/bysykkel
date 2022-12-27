from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class StationInfo(BaseModel):
    """Payload with information on an Oslo Bysykkel bike station.

    References:
        Oslo Bysykkel ("Stasjoner"): https://oslobysykkel.no/apne-data/sanntid
        GBFS station_information.json: https://github.com/MobilityData/gbfs/blob/df473ca4adbff982d67b50ac00b625191591d8f8/gbfs.md#station_informationjson
    """

    station_id: str
    name: str
    address: Optional[str]
    lat: float
    lon: float
    capacity: int


class StationInfos(BaseModel):
    stations: List[StationInfo]


class StationInfoResponse(BaseModel):
    """Payload with metadata for all Oslo Bysykkel bike stations.

    References:
        Oslo Bysykkel ("Stasjoner"): https://oslobysykkel.no/apne-data/sanntid
        GBFS station_information.json: https://github.com/MobilityData/gbfs/blob/df473ca4adbff982d67b50ac00b625191591d8f8/gbfs.md#station_informationjson
    """

    last_updated: datetime
    data: StationInfos


class StationStatus(BaseModel):
    """Payload with timestamped status of an Oslo Bysykkel bike station.

    References:
        Oslo Bysykkel ("Tilgjengelighet"): https://oslobysykkel.no/apne-data/sanntid
        GBFS station_status.json: https://github.com/MobilityData/gbfs/blob/df473ca4adbff982d67b50ac00b625191591d8f8/gbfs.md#station_statusjson
    """

    station_id: str
    is_installed: int
    is_renting: int
    is_returning: int
    num_bikes_available: int
    num_docks_available: int
    last_reported: datetime


class StationStatuses(BaseModel):
    stations: List[StationStatus]


class StationStatusReponse(BaseModel):
    """Payload with timestamped status of all Oslo Bysykkel bike stations.

    References:
        Oslo Bysykkel ("Stasjoner"): https://oslobysykkel.no/apne-data/sanntid
        GBFS station_information.json: https://github.com/MobilityData/gbfs/blob/df473ca4adbff982d67b50ac00b625191591d8f8/gbfs.md#station_informationjson
    """

    last_updated: datetime
    data: StationStatuses
