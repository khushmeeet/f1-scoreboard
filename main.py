import json
from datetime import datetime, timezone
import ergast_py
from fastapi.param_functions import Depends
import httpx
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from filters import datetime_format, laptime_format, race_status_str, combine_date_time
from httpx_client import HTTPXClient
from models import ScheduleModel
from consts import RACE_SCHEDULE_URL
from utils import get_schedule

# TODO:
#   Add time interval


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


@app.get("/", response_class=HTMLResponse)
async def race_results(req: Request):
    race = e.season().round().get_results()
    quali = e.season().round().get_qualifyings()
    return templates.TemplateResponse(
        "race_results.html", {"request": req, "race": race[0], "quali": quali[0]}
    )


@app.get("/schedule", response_class=HTMLResponse)
async def race_schedule(req: Request, httpx_c=Depends(client)):
    schedule = await httpx_c.get(RACE_SCHEDULE_URL)
    schedule = json.loads(schedule.content)
    schedule = get_schedule(schedule)
    print(schedule)
    return templates.TemplateResponse(
        "schedule.html", {"request": req, "schedule": schedule}
    )
