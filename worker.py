import json
import os
import time
import random
import string

def create_riot_account(task_id, user_data_dir):

    os.makedirs("results", exist_ok=True)

    time.sleep(3)

    username = "user" + "".join(random.choices(string.digits, k=5))
    password = "Pass" + "".join(random.choices(string.digits, k=5)) + "!"

    result = {
        "task_id": task_id,
        "status": "success",
        "account_info": {
            "username": username,
            "password": password,
            "email": f"{username}@mail.com",
            "dob": "12/12/2002"
        },
        "error": None
    }

    with open(f"results/{task_id}.json", "w") as f:
        json.dump(result, f)
