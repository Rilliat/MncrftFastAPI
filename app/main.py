import subprocess

from fastapi import FastAPI
from utils import validate_token
import os


app = FastAPI()

strings = {
    'invalid_token': {
        'status': 'fail',
        'result': 'Invalid token',
    },
    'home': {
        'message': 'Hello on home page!',
    },
}
string_result = {
        'status': 'success',
        'output': '{}',
    }


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
    result = string_result['output'].format(result)
    return result
