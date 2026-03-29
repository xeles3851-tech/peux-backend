from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from multiprocessing import Process
import uuid
import os
import json
from typing import Optional
import logging

app = FastAPI()

# Configure CORS to allow requests from PHP frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(filename="api.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class TaskResponse(BaseModel):
    task_id: str
    status: str
    account_info: Optional[dict] = None
    error: Optional[str] = None

@app.get("/create-account", response_model=TaskResponse)
async def create_account():
    task_id = str(uuid.uuid4())
    try:
        user_data_dir = f"user_data_{task_id}"
        # Import worker here to avoid import issues in multiprocessing
        from worker import create_riot_account
        process = Process(target=create_riot_account, args=(task_id, user_data_dir))
        process.start()
        logging.info(f"Started worker process for task {task_id} with user_data_dir {user_data_dir}")
        return TaskResponse(task_id=task_id, status="queued")
    except Exception as e:
        logging.error(f"Failed to start worker for task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start worker: {str(e)}")

@app.get("/task/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str):
    result_file = f"results/{task_id}.json"
    if not os.path.exists(result_file):
        raise HTTPException(status_code=404, detail="Task not found or still processing")
    
    try:
        with open(result_file, "r") as f:
            result = json.load(f)
        return TaskResponse(**result)
    except json.JSONDecodeError:
        logging.error(f"Corrupted result file for task {task_id}")
        raise HTTPException(status_code=500, detail="Result file is corrupted")
    except Exception as e:
        logging.error(f"Unexpected error for task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    os.makedirs("results", exist_ok=True)
    uvicorn.run(app, host="0.0.0.0", port=8000)
