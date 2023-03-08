import ergast_py
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
e = ergast_py.Ergast()


@app.get("/", response_class=HTMLResponse)
async def race_results(req: Request):
    data = e.season().round().get_results()
    return templates.TemplateResponse(
        "race_results.html", {"request": req, "data": data[0]}
    )
