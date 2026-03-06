from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import logging, json, os

from db import connect, select_all, insert_one, update_one
from model_whitelist import TABLES

app = FastAPI()
templates = Jinja2Templates(directory="templates")

logging.basicConfig(filename="auth.log", level=logging.INFO)

db_conn = None


def require_login():
    if db_conn is None:
        return False
    return True


@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(user: str = Form(...), password: str = Form(...)):
    global db_conn

    params = {
        "user": user,
        "password": password,
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "dbname": os.getenv("POSTGRES_DB")
    }

    db_conn = connect(params)

    if db_conn is None:
        logging.warning(f"FAILED LOGIN {user}")
        return RedirectResponse("/", status_code=302)

    return RedirectResponse("/index", status_code=302)


@app.get("/index", response_class=HTMLResponse)
def index(request: Request):

    if not require_login():
        return RedirectResponse("/", status_code=302)

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "tables": TABLES.keys()}
    )


@app.get("/tables/{table}", response_class=HTMLResponse)
def view_table(request: Request, table: str):

    if not require_login():
        return RedirectResponse("/", status_code=302)

    data = select_all(db_conn, table, TABLES)

    if data is None:
        data = []

    return templates.TemplateResponse(
        "tables.html",
        {"request": request, "rows": data, "table": table}
    )


@app.get("/insert/{table}", response_class=HTMLResponse)
def insert_page(request: Request, table: str):

    if not require_login():
        return RedirectResponse("/", status_code=302)

    return templates.TemplateResponse(
        "insert.html",
        {"request": request, "table": table}
    )


@app.post("/insert/{table}")
def insert(table: str, json_data: str = Form(...)):

    if not require_login():
        return RedirectResponse("/", status_code=302)

    try:
        insert_one(db_conn, table, json.loads(json_data), TABLES)
    except Exception as e:
        logging.error(e)

    return RedirectResponse(f"/tables/{table}", status_code=302)


@app.get("/update/{table}/{row_id}", response_class=HTMLResponse)
def update_page(request: Request, table: str, row_id: int):

    if not require_login():
        return RedirectResponse("/", status_code=302)

    rows = select_all(db_conn, table, TABLES)

    if not rows:
        return RedirectResponse(f"/tables/{table}", status_code=302)

    row = None
    for r in rows:
        if r.get("id") == row_id:
            row = r
            break

    if row is None:
        return RedirectResponse(f"/tables/{table}", status_code=302)

    return templates.TemplateResponse(
        "update.html",
        {"request": request, "table": table, "row": row}
    )


@app.post("/update/{table}")
def update(table: str, row_id: int = Form(...), json_data: str = Form(...)):

    if not require_login():
        return RedirectResponse("/", status_code=302)

    try:
        update_one(db_conn, table, row_id, json.loads(json_data), TABLES)
    except Exception as e:
        logging.error(e)

    return RedirectResponse(f"/tables/{table}", status_code=302)