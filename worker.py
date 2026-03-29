import os
import json
import time
import random
import string
import logging

logging.basicConfig(
    filename="worker.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def generate_password():
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(12)) + "!"

def generate_username():
    return "demo_" + "".join(random.choice(string.digits) for _ in range(6))

def create_demo_account(task_id, user_data_dir):
    logging.info(f"Starting demo task {task_id}")
    os.makedirs("results", exist_ok=True)

    result = {
        "task_id": task_id,
        "status": "failed",
        "account_info": {},
        "error": None
    }

    try:
        time.sleep(3)

        account_info = {
            "username": generate_username(),
            "password": generate_password(),
            "dob": "12/12/2002",
            "email": f"{task_id[:8]}@example.com",
            "verifier": "demo"
        }

        result["status"] = "success"
        result["account_info"] = account_info

        logging.info(f"Task {task_id} SUCCESS")

    except Exception as e:
        result["error"] = str(e)
        logging.error(f"Task {task_id} FAILED: {str(e)}")

    with open(f"results/{task_id}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    import sys
    task_id = sys.argv[1] if len(sys.argv) > 1 else "manual"
    create_demo_account(task_id, f"user_data_{task_id}")
