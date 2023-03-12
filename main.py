import json
from functools import lru_cache
from datetime import datetime, timezone
import ergast_py
from fastapi import FastAPI, Request
from fastapi.param_functions import Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from httpx_client import HTTPXClient
from filters import (
    datetime_format,
    laptime_format,
    race_status_str,
    combine_date_time,
    is_failure,
)
from utils import get_schedule
import asciichartpy

# TODO:
#   Add time interval
#   Fix https issue

RACE_SCHEDULE_URL = "http://ergast.com/api/f1/current.json"

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
templates.env.globals["now"] = datetime.now(timezone.utc).astimezone()
templates.env.filters["datetime_format"] = datetime_format
templates.env.filters["laptime_format"] = laptime_format
templates.env.filters["race_status"] = race_status_str
templates.env.filters["combine_date_time"] = combine_date_time
templates.env.filters["is_failure"] = is_failure

e = ergast_py.Ergast()
client = HTTPXClient()


@app.on_event("startup")
async def startup():
    client.start()


@app.on_event("shutdown")
async def shutdown():
    await client.stop()


@lru_cache
def ergast_results(*args) -> list:
    result = e
    for arg in args:
        if isinstance(arg, str):
            result = getattr(result, arg)()
        else:
            method_name, method_args = arg
            result = getattr(result, method_name)(*method_args)
    return result


def last_six_seasons() -> list:
    current_year = datetime.now().year
    return [i for i in range(current_year - 1, current_year - 7, -1)]


def total_constructor_points(constructor):
    constructor_points = {}
    if isinstance(constructor, dict):
        for k, v in constructor.items():
            points = 0
            for race in v:
                for j in race.results:
                    points += j.points
            constructor_points[k] = {
                "total_points": points,
                "constructor_name": v[0].results[0].constructor.name,
                "drivers": [
                    v[0].results[0].driver.given_name
                    + " "
                    + v[0].results[0].driver.family_name,
                    v[0].results[1].driver.given_name
                    + " "
                    + v[0].results[1].driver.family_name,
                ],
            }
    else:
        for race in constructor:
            points = 0
            for j in race.results:
                points += j.points
            constructor_points[race.season] = {
                "total_points": points,
                "constructor_name": race.results[0].constructor.name,
                "drivers": [
                    race.results[0].driver.given_name
                    + " "
                    + race.results[0].driver.family_name,
                    race.results[1].driver.given_name
                    + " "
                    + race.results[1].driver.family_name,
                ],
            }
    return constructor_points


@app.get("/", response_class=HTMLResponse)
async def race_results(req: Request):
    race = ergast_results("season", "round", "get_results")
    quali = ergast_results("season", "round", "get_qualifyings")
    return templates.TemplateResponse(
        "race-results.html", {"request": req, "race": race[0], "quali": quali[0]}
    )


@app.get("/schedule", response_class=HTMLResponse)
async def race_schedule(req: Request, httpx_c=Depends(client)):
    schedule = await httpx_c.get(RACE_SCHEDULE_URL)
    schedule = json.loads(schedule.content)
    schedule = get_schedule(schedule)
    return templates.TemplateResponse(
        "schedule.html", {"request": req, "schedule": schedule}
    )


@app.get("/drivers", response_class=HTMLResponse)
async def drivers(req: Request):
    drivers = ergast_results("season", "get_driver_standings")
    return templates.TemplateResponse(
        "drivers.html", {"request": req, "drivers": drivers}
    )


@app.get("/drivers/{driver_id}", response_class=HTMLResponse)
async def driver(req: Request, driver_id: str):
    driver_details = ergast_results("season", ("driver", (driver_id,)), "get_results")
    points = [d.results[0].points for d in driver_details]
    plot = (
        None
        if len(points) <= 1
        else asciichartpy.plot(points, {"height": 8, "format": "{:8.0f}"})
    )
    past_year_details = {
        i: ergast_results(("season", (i,)), ("driver", (driver_id,)), "get_results")
        for i in last_six_seasons()
    }
    return templates.TemplateResponse(
        "single-driver.html",
        {
            "request": req,
            "driver": driver_details,
            "plot": plot,
            "past_year": past_year_details,
        },
    )


@app.get("/constructors", response_class=HTMLResponse)
async def constructors(req: Request):
    constructors = ergast_results("season", "get_constructor_standings")
    return templates.TemplateResponse(
        "constructors.html", {"request": req, "constructors": constructors}
    )


@app.get("/constructors/{constructor_id}", response_class=HTMLResponse)
async def constructor(req: Request, constructor_id: str):
    constructor_details = ergast_results(
        "season", ("constructor", (constructor_id,)), "get_results"
    )
    past_year_details = {
        i: ergast_results(
            ("season", (i,)), ("constructor", (constructor_id,)), "get_results"
        )
        for i in last_six_seasons()
    }
    past_year_details = total_constructor_points(past_year_details)
    this_year_details = total_constructor_points(constructor_details)
    print(this_year_details)

    return templates.TemplateResponse(
        "single-constructor.html",
        {
            "request": req,
            "constructor": this_year_details,
            "past_year": past_year_details,
        },
    )
