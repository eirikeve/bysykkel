import logging

from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi import status
import httpx
from dotenv import load_dotenv

from bysykkel.client import BysykkelClient
from bysykkel.models import StationData, PartialStationData
from bysykkel.app.config import Settings


load_dotenv()

logging.basicConfig()
logger = logging.getLogger(__name__)
settings = Settings()  # type: ignore

app = FastAPI(title=settings.app_name)


def client():
    client_identifier = f"eirikeve-bysykkel-{settings.env}"
    return BysykkelClient(
        settings.oslobysykkel_apiurl, client_identifier=client_identifier
    )


def _filter_predicate(field: str, comparison: str):
    if comparison.startswith("<="):
        value = int(comparison[2:])
        return lambda x: getattr(x, field) <= value
    if comparison.startswith("<"):
        value = int(comparison[1:])
        return lambda x: getattr(x, field) < value
    elif comparison.startswith(">="):
        value = int(comparison[2:])
        return lambda x: getattr(x, field) >= value
    elif comparison.startswith(">"):
        value = int(comparison[1:])
        return lambda x: getattr(x, field) > value

    value = int(comparison)
    return lambda x: getattr(x, field) == value


def filter_predicate(field: str, comparison: str):
    """Create a function that performs a numeric comparison on an object field.

    Example:
        >>> filter_predicate("foo", ">=10") # predicate to check if `.foo` is >= 10


    """
    try:
        return _filter_predicate(field, comparison)
    except ValueError as e:
        logging.warning(f"Caught exception due to unsupported filter: {e}")
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, f"Unsupported filter {field}{comparison}"
        )


@app.get(
    "/v1/stations",
    response_model=List[PartialStationData],
    response_model_exclude_defaults=True,
    # TODO: Update responses here so the OpenAPI doc includes all status codes.
)
async def get_stations(
    fields: Optional[str] = None,
    limit: Optional[int] = None,
    num_bikes_available: Optional[str] = None,
    num_docks_available: Optional[str] = None,
    client: BysykkelClient = Depends(client),
):
    """Get a list of city bike stations, optionally filtering the list and picking a subset of the station fields.

    Parameters
    ==========
    - `fields`: An optional comma-separated list of fields to return for each city bike station object. Example: `station_id,num_bikes_available`
    - `limit`: An optional integer indicating the maximum number of city bike stations to return. Example: `10`
    - `num_bikes_available`: An optional integer or comparison (<=, <, >=, >) followed by an integer to filter the city bike stations
        by how many bikes they currently have available. Example: `>=5` or `<10`
    - `num_docks_available`: An optional integer or comparison (<=, <, >=, >) followed by an integer to filter the city bike stations
        by how many free docks they currently have available. Example: `>=5` or `0`

    Response codes
    ==============
    - `200`: Successful response
    - `400`: Unsupported filter query
    - `503`: Connection to Oslo Bysykkel's API failed
    """

    filters = []
    if num_bikes_available:
        filters.append(filter_predicate("num_bikes_available", num_bikes_available))
    if num_docks_available:
        filters.append(filter_predicate("num_docks_available", num_docks_available))

    # This fetches both the metadata, and the current status/availability for all stations.
    try:
        stations: List[StationData] = await client.get_stations()
    except httpx.NetworkError as e:
        logger.warning(f"Caught exception due to connection error: {e}")
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Failed to connect to Oslo Bysykkel's API",
        )

    if filters:
        stations = [
            station
            for station in stations
            if all(filter(station) for filter in filters)
        ]

    if fields:
        field_names = set(fields.split(","))
        filtered_station_data = [
            {k: v for k, v in station.dict().items() if k in field_names}
            for station in stations
        ]
        stations = [PartialStationData(**data) for data in filtered_station_data]

    if limit:
        return stations[:limit]
    return stations


@app.get("/v1/station/{id}", response_model=StationData)
async def get_station(
    id: str,
    client: BysykkelClient = Depends(client),
):
    """Get a single city bike station's data by id.

    Parameters
    ==========
    - `id`: Route parameter to pick the station. Corresponds to `station_id` in the objects from the `/v1/stations` route.

    Response codes
    ==============
    - `200`: Successful response
    - `404`: Station `id` not found
    - `503`: Connection to Oslo Bysykkel's API failed
    """

    # TODO: This is pretty reduntant: we're fetching data for all the stations.
    #       Might want to optimize it to avoid unnecessary load on Oslo Bysykkel's API,
    #       e.g. by leveraging some form of caching
    try:
        stations: List[StationData] = await client.get_stations()
    except httpx.NetworkError as e:
        logger.warning(f"Caught exception due to connection error: {e}")
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Failed to connect to Oslo Bysykkel's API",
        )

    for station in stations:
        # TODO: We already order the stations by id in the client,
        # if we expose that dict we could get rid of this loop
        if station.station_id == id:
            return station
    raise HTTPException(404, detail=f"Station not found: {id}")


@app.get("/live")
def live():
    "Liveness probe"
    return {"live": True}


@app.get("/ready")
def ready():
    "Readiness probe"
    # No setup required as the app is stateless.
    return {"ready": True}


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


if __name__ == "__main__":
    import uvicorn

    # TODO: Uvicorn isn't suited for prod, should be updated to use gunicorn in prod
    uvicorn.run(app, host=settings.host, port=settings.port)
