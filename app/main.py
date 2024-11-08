import subprocess

from fastapi import FastAPI
from utils import json_to_dict_list, validate_token
import os
from typing import Optional

# Получаем путь к директории текущего скрипта
script_dir = os.path.dirname(os.path.abspath(__file__))

# Переходим на уровень выше
parent_dir = os.path.dirname(script_dir)

# Получаем путь к JSON
path_to_json = os.path.join(parent_dir, 'students.json')

app = FastAPI()


@app.get("/students")
def get_all_students():
    return json_to_dict_list(path_to_json)

@app.get("/")
def home_page():
    return {"message": "Hello on home page!"}

@app.get("/get_status")
def get_status(token: str, service: str):
    if validate_token(token):
        result = subprocess.run(["systemctl", "status", service if service.endswith('.service') else service+'.service'])
        result = result.stdout
        return {
            "status": "ok",
            "result": result,
        }
