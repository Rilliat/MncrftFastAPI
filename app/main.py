import subprocess

from fastapi import FastAPI, responses
from utils import validate_token


app = FastAPI()

strings = {
    'invalid_token': {
        'status': 'fail',
        'result': 'Invalid token',
    },
    'home': 'Hello on home page!',
}


@app.get("/")
def home_page():
    return responses.PlainTextResponse(strings['home'])

@app.get("/get_status")
def get_status(token: str, service: str):
    if not validate_token(token):
        return strings['invalid_token']

    result = subprocess.run(["systemctl", "is-active", service if service.endswith('.service') else service+'.service'],
                            capture_output=True, text=True)
    result = result.stdout.replace('\n', '')
    return {
        'status': 'success',
        'output': result,
    }
