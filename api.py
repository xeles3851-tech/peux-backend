from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse  # KRİTİK EKSİK BUYDU
from pydantic import BaseModel
from threading import Thread
from typing import Optional
import uuid
import os
import json
import logging
import uvicorn

app = FastAPI()

os.makedirs("results", exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskResponse(BaseModel):
    task_id: str
    status: str
    account_info: Optional[dict] = None
    error: Optional[str] = None

# TASARIMIN AÇILMASI İÇİN BURASI ŞART
@app.get("/")
def home():
    return FileResponse("index.html")

@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)

@app.get("/create-account", response_model=TaskResponse)
def create_account():
    task_id = str(uuid.uuid4())
    user_data_dir = f"user_data_{task_id}"
    try:
        from worker import create_riot_account
        thread = Thread(
            target=create_riot_account,
            args=(task_id, user_data_dir),
            daemon=True
        )
        thread.start()
        return TaskResponse(task_id=task_id, status="queued")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/task/{task_id}", response_model=TaskResponse)
def get_task_status(task_id: str):
    result_file = f"results/{task_id}.json"
    if not os.path.exists(result_file):
        raise HTTPException(status_code=404, detail="Islem devam ediyor...")
    with open(result_file, "r", encoding="utf-8") as f:
        result = json.load(f)
    return TaskResponse(**result)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
