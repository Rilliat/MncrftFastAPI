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

strings = {
    'invalid_token': {
        'status': 'fail',
        'result': 'Invalid token',
    },
    'home': {
        'message': 'Hello on home page!',
    },
    'result': {
        'status': 'success',
        'result': '{}',
    },

}


@app.get("/students")
def get_all_students():
    return json_to_dict_list(path_to_json)

@app.get("/")
def home_page():
    return strings['home']

@app.get("/get_status")
def get_status(token: str, service: str):
    if not validate_token(token):
        return strings['invalid_token']

    result = subprocess.run(["systemctl", "is-active", service if service.endswith('.service') else service+'.service'],
                            capture_output=True, text=True)
    result = result.stdout.replace('\n', '')
    return strings['result'].__format__(result)

