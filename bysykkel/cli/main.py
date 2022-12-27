import asyncio

from pydantic import AnyUrl
from rich.table import Table
from rich.console import Console
from rich import box

import typer

from bysykkel.client import BysykkelClient

app = typer.Typer(name="bysykkel")


@app.callback()
def create_client(
    ctx: typer.Context,
    base_url: str = "https://gbfs.urbansharing.com/oslobysykkel.no",
):

    client = BysykkelClient(base_url)
    ctx.obj = client


@app.command("list")
def list_stations(ctx: typer.Context, pretty: bool = False):
    client: BysykkelClient = ctx.obj
    stations = asyncio.run(client.get_stations())

    table = Table(title="Bysykler", box=box.MINIMAL_DOUBLE_HEAD if pretty else None)
    table.add_column("Stativ")
    table.add_column("Adresse")
    table.add_column("# Sykler")
    table.add_column("# Låser")

    for station in stations:
        table.add_row(
            station.name,
            station.address,
            str(station.num_bikes_available),
            str(station.num_docks_available),
        )

    Console().print(table)


if __name__ == "__main__":
    app()
