from typing import Literal, List

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseSettings, AnyUrl
from dotenv import load_dotenv

from bysykkel.client import BysykkelClient
from bysykkel.models import StationData
from bysykkel.app.config import Settings


load_dotenv()

settings = Settings()  # type: ignore

app = FastAPI(title=settings.app_name)


def client():
    return BysykkelClient(settings.oslobysykkel_apiurl)


@app.get("/v1/stations", response_model=List[StationData])
async def get_stations(client: BysykkelClient = Depends(client)):
    return await client.get_stations()


@app.get("/v1/station/{id}", response_model=StationData)
async def get_station(id: str, client: BysykkelClient = Depends(client)):
    stations = await client.get_stations()
    for station in stations:
        # TODO: We already order the stations by id in the client,
        # if we expose that dict we could get rid of this loop
        if station.station_id == id:
            return station
    raise HTTPException(404, detail=f"Station not found: {id}")


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.host, port=settings.port)
