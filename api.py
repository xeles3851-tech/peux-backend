from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from threading import Thread
import uuid
import os
import json
from typing import Optional
import logging

app = FastAPI()

# results klasörü garanti oluştur
os.makedirs("results", exist_ok=True)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# logging
logging.basicConfig(
    filename="api.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

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

        # worker import
        from worker import create_riot_account

        # THREAD başlat
        thread = Thread(
            target=create_riot_account,
            args=(task_id, user_data_dir)
        )
        thread.start()

        logging.info(f"Worker thread started for task {task_id}")

        return TaskResponse(
            task_id=task_id,
            status="queued"
        )

    except Exception as e:
        logging.error(f"Worker başlatılamadı: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Worker başlatılamadı: {str(e)}"
        )


@app.get("/task/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str):

    result_file = f"results/{task_id}.json"

    if not os.path.exists(result_file):
        raise HTTPException(
            status_code=404,
            detail="Task hala çalışıyor veya bulunamadı"
        )

    try:
        with open(result_file, "r") as f:
            result = json.load(f)

        return TaskResponse(**result)

    except json.JSONDecodeError:
        logging.error(f"Corrupted result file: {task_id}")
        raise HTTPException(
            status_code=500,
            detail="Result file bozuk"
        )

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
