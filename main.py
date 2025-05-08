from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# In-memory database simulation
tasks_db = []
task_id_counter = 1

# Pydantic models
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool

# CRUD operations
async def create_task(task: TaskCreate) -> TaskResponse:
    global task_id_counter
    new_task = {
        "id": task_id_counter,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
    }
    tasks_db.append(new_task)
    task_id_counter += 1
    return TaskResponse(**new_task)

async def get_tasks() -> List[TaskResponse]:
    return [TaskResponse(**task) for task in tasks_db]

async def get_task(task_id: int) -> Optional[TaskResponse]:
    for task in tasks_db:
        if task["id"] == task_id:
            return TaskResponse(**task)
    return None

async def update_task(task_id: int, task: TaskCreate) -> Optional[TaskResponse]:
    for existing_task in tasks_db:
        if existing_task["id"] == task_id:
            existing_task.update(
                title=task.title,
                description=task.description,
                completed=task.completed,
            )
            return TaskResponse(**existing_task)
    return None

async def delete_task(task_id: int) -> bool:
    global tasks_db
    for task in tasks_db:
        if task["id"] == task_id:
            tasks_db = [t for t in tasks_db if t["id"] != task_id]
            return True
    return False

# API endpoints
@app.post("/tasks/", response_model=TaskResponse)
async def add_task(task: TaskCreate):
    return await create_task(task)

@app.get("/tasks/", response_model=List[TaskResponse])
async def read_tasks():
    return await get_tasks()

@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def read_task(task_id: int):
    task = await get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_existing_task(task_id: int, task: TaskCreate):
    updated_task = await update_task(task_id, task)
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task

@app.delete("/tasks/{task_id}", status_code=204)
async def delete_existing_task(task_id: int):
    result = await delete_task(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")