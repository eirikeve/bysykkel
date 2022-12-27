import os

from fastapi.testclient import TestClient
import httpx
import pytest


from bysykkel.app.main import app


@pytest.fixture(scope="session")
def client():

    test_host = os.getenv("BYSYKKEL_E2E_TEST_HOST")
    if not test_host:
        # Run tests directly against the FastAPI ASGI app
        return TestClient(app)

    # ... or, run tests against a (possibly remote) server hosting the app
    class IntegrationTestClient:
        def __init__(self, base_url: str) -> None:
            self.base_url = base_url.removesuffix("/")

        def get(self, path_query: str):
            path_query = path_query.removeprefix("/")
            url = f"{self.base_url}/{path_query}"
            return httpx.get(url)

    return IntegrationTestClient(test_host)


@pytest.fixture(scope="session")
def stations_response(client):
    "Cache the request response for the duration of this test session"


def test_has_live_route(client: TestClient):
    response = client.get("/live")
    assert response.status_code == 200


def test_has_ready_route(client: TestClient):
    response = client.get("/live")
    assert response.status_code == 200


def test_list_stations_route_responds_200(client: TestClient):
    response = client.get("/v1/stations")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert 0 < len(body)


def test_stations_route_supports_picking_fields(client: TestClient):
    fields = set(["station_id", "num_bikes_available"])
    response = client.get("/v1/stations?fields=" + ",".join(fields))

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert all(set(station.keys()) == fields for station in body)


def test_stations_route_filtering_supports_min_available_bikes(client: TestClient):
    min_bikes_available = 5
    response = client.get(f"/v1/stations?num_bikes_available=>{min_bikes_available}")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert all(
        station["num_bikes_available"] >= min_bikes_available for station in body
    )


def test_stations_route_filtering_supports_min_available_docks(client: TestClient):
    min_docks_available = 5
    response = client.get(f"/v1/stations?num_docks_available=>{min_docks_available}")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert all(
        station["num_docks_available"] >= min_docks_available for station in body
    )


def test_stations_route_filtering_invalid_query_results_in_400_response(
    client: TestClient,
):
    min_docks_available = 5
    response = client.get(f"/v1/stations?num_docks_available=>>{min_docks_available}")
    assert response.status_code == 400


def test_stations_route_supports_limit_count_returned(
    client: TestClient,
):
    limit = 5
    response = client.get(f"/v1/stations?limit={limit}&fields=station_id")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) <= limit
