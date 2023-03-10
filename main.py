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
from filters import datetime_format, laptime_format, race_status_str, combine_date_time
from utils import get_schedule

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

e = ergast_py.Ergast()
client = HTTPXClient()


@app.on_event("startup")
async def startup():
    client.start()


@app.on_event("shutdown")
async def shutdown():
    await client.stop()


@lru_cache
def ergast_results(*args):
    result = e
    for arg in args:
        if isinstance(arg, str):
            result = getattr(result, arg)()
        else:
            method_name, method_args = arg
            result = getattr(result, method_name)(*method_args)
    return result


@app.get("/", response_class=HTMLResponse)
async def race_results(req: Request):
    race = ergast_results("season", "round", "get_results")
    quali = ergast_results("season", "round", "get_qualifyings")
    print(quali)
    return templates.TemplateResponse(
        "race_results.html", {"request": req, "race": race[0], "quali": quali[0]}
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


@app.get("/constructors", response_class=HTMLResponse)
async def constructors(req: Request):
    constructors = ergast_results("season", "get_constructor_standings")
    return templates.TemplateResponse(
        "constructors.html", {"request": req, "constructors": constructors}
    )
