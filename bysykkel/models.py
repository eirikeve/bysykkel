from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class StationInfo(BaseModel):
    """Payload with information on an Oslo Bysykkel bike station.

    The fields are a subset of GBFS "station_information.json"

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


class StationStatus(BaseModel):
    """Payload with timestamped status of an Oslo Bysykkel bike station.

    The fields are a subset of GBFS "station_status.json"

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
