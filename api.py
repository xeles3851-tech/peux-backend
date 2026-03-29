from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def home():
    return {"message": "site calisiyor"}

@app.get("/ping")
def ping():
    return {"ping": "pong"}
