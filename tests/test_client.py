import httpx
import pytest
import respx

from bysykkel.client import BysykkelClient
from bysykkel.models import StationInfoResponse, StationStatusReponse


@pytest.fixture
def system_information_response():
    """Example response from https://oslobysykkel.no/en/open-data/realtime"""
    url = "https://gbfs.urbansharing.com/oslobysykkel.no/station_information.json"
    body = {
        "last_updated": 1553592653,
        "data": {
            "stations": [
                {
                    "station_id": "627",
                    "name": "Skøyen Stasjon",
                    "address": "Skøyen Stasjon",
                    "lat": 59.9226729,
                    "lon": 10.6788129,
                    "capacity": 20,
                },
                {
                    "station_id": "623",
                    "name": "7 Juni Plassen",
                    "address": "7 Juni Plassen",
                    "lat": 59.9150596,
                    "lon": 10.7312715,
                    "capacity": 15,
                },
                {
                    "station_id": "610",
                    "name": "Sotahjørnet",
                    "address": "Sotahjørnet",
                    "lat": 59.9099822,
                    "lon": 10.7914482,
                    "capacity": 20,
                },
            ]
        },
    }

    return {"url": url, "body": body}


@pytest.fixture
def system_status_response():
    """Example response from https://oslobysykkel.no/en/open-data/realtime"""
    url = "https://gbfs.urbansharing.com/oslobysykkel.no/station_status.json"
    body = {
        "last_updated": 1540219230,
        "data": {
            "stations": [
                {
                    "is_installed": 1,
                    "is_renting": 1,
                    "num_bikes_available": 7,
                    "num_docks_available": 5,
                    "last_reported": 1540219230,
                    "is_returning": 1,
                    "station_id": "175",
                },
                {
                    "is_installed": 1,
                    "is_renting": 1,
                    "num_bikes_available": 4,
                    "num_docks_available": 8,
                    "last_reported": 1540219230,
                    "is_returning": 1,
                    "station_id": "47",
                },
                {
                    "is_installed": 1,
                    "is_renting": 1,
                    "num_bikes_available": 4,
                    "num_docks_available": 9,
                    "last_reported": 1540219230,
                    "is_returning": 1,
                    "station_id": "10",
                },
            ]
        },
    }

    return {"url": url, "body": body}


def test_bysykkelclient_instantiates():
    client = BysykkelClient("http://localhost")


@respx.mock
@pytest.mark.asyncio
async def test_bysykkelclient_can_list_station_information(system_information_response):
    url, body = system_information_response["url"], system_information_response["body"]
    mock = respx.get(url).mock(return_value=httpx.Response(200, json=body))

    client = BysykkelClient("https://gbfs.urbansharing.com/oslobysykkel.no")

    info: StationInfoResponse = await client.get_station_information()
    assert 3 == len(info.data.stations)
    assert any(station.capacity > 0 for station in info.data.stations)


@respx.mock
@pytest.mark.asyncio
async def test_bysykkelclient_can_list_station_status(system_status_response):
    url, body = system_status_response["url"], system_status_response["body"]
    mock = respx.get(url).mock(return_value=httpx.Response(200, json=body))

    client = BysykkelClient("https://gbfs.urbansharing.com/oslobysykkel.no")

    status: StationStatusReponse = await client.get_station_status()
    assert 3 == len(status.data.stations)
    assert any(station.num_bikes_available > 0 for station in status.data.stations)
