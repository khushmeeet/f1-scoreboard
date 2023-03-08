from datetime import datetime, timezone
import ergast_py
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from filters import datetime_format, laptime_format, race_status_str

# TODO:
#   Add time interval


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
templates.env.globals["now"] = datetime.now(timezone.utc).astimezone()
templates.env.filters["datetime_format"] = datetime_format
templates.env.filters["laptime_format"] = laptime_format
templates.env.filters["race_status"] = race_status_str

e = ergast_py.Ergast()


@app.get("/", response_class=HTMLResponse)
async def race_results(req: Request):
    data = e.season().round().get_results()
    print(data)
    return templates.TemplateResponse(
        "race_results.html", {"request": req, "data": data[0]}
    )
