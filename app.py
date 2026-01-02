from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from typing import Optional
import json
import os

app = FastAPI()

# Templates & static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

DATA_FILE = "data/tasks.json"



def get_data():
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []


def save_data(tasks):
    with open(DATA_FILE, "w") as file:
        json.dump(tasks, file, indent=2)


def get_next_id(tasks):
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1




@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        "homepage.html",
        {"request": request}
    )


@app.get("/tasks")
def view_tasks(request: Request):
    tasks = get_data()
    return templates.TemplateResponse(
        "tasks.html",
        {
            "request": request,
            "tasks": tasks
        }
    )


@app.get("/create")
def create_task_page(request: Request):
    return templates.TemplateResponse(
        "create_task.html",
        {"request": request}
    )


@app.post("/tasks/create")
def create_task(
    title: str = Form(...),
    description: str = Form(...),
    completed: Optional[str] = Form(None)
):
    tasks = get_data()

    new_task = {
        "id": get_next_id(tasks),
        "title": title,
        "description": description,
        "completed": True if completed else False
    }

    tasks.append(new_task)
    save_data(tasks)

    return RedirectResponse(url="/tasks", status_code=303)


@app.get("/delete")
def delete_tasks_page(request: Request):
    tasks = get_data()
    return templates.TemplateResponse(
        "delete_tasks.html",
        {
            "request": request,
            "tasks": tasks
        }
    )


@app.post("/tasks/delete")
def delete_task(task_id: int = Form(...)):
    tasks = get_data()
    tasks = [task for task in tasks if task["id"] != task_id]
    save_data(tasks)

    return RedirectResponse(url="/tasks", status_code=303)
