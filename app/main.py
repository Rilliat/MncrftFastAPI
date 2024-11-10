import subprocess

from fastapi import FastAPI, responses
from utils import validate_token


app = FastAPI()

strings = {
    'invalid_token': {
        'status': 'fail',
        'result': 'Invalid token',
    },
    'success': {
        'status': 'success',
        'result': 'Success',
    },
    'error': 'Error occurred: {}',
    'home': 'Hello on home page!',
}


def _get_unit_pid(unit: str) -> str:
    return (
        subprocess.run(
            ["systemctl",
                "show",
                unit,
                "--property=MainPID",
                "--value",
            ],
            check=False,
            stdout=subprocess.PIPE,
        )
        .stdout.decode()
        .strip()
    )

def human_readable_size(size: float, decimal_places: int = 2) -> str:
    for unit in ["B", "K", "M", "G", "T", "P"]:
        if size < 1024.0 or unit == "P":
            break
        size /= 1024.0

    return f"{size:.{decimal_places}f} {unit}"



@app.get("/")
def home_page():
    return responses.PlainTextResponse(strings['home'])

@app.get("/status")
def status(token: str, service: str):
    if not validate_token(token):
        return strings['invalid_token']

    result = subprocess.run(["systemctl", "is-active", service if service.endswith('.service') else service+'.service'],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = result.stdout.decode().replace('\n', '')
    return {
        'status': 'success',
        'output': result,
    }

@app.get("/start")
def start(token: str, service: str):
    if not validate_token(token):
        return strings['invalid_token']

    try:
        subprocess.run(["systemctl", "start", service], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return strings['success']
    except Exception as e:
        return responses.PlainTextResponse(strings['error'].format(e), status_code=500)

@app.get("/stop")
def stop(token: str, service: str):
    if not validate_token(token):
        return strings['invalid_token']

    try:
        subprocess.run(["systemctl", "stop", service], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return strings['success']
    except Exception as e:
        return responses.PlainTextResponse(strings['error'].format(e), status_code=500)


@app.get("/restart")
def restart(token: str, service: str):
    if not validate_token(token):
        return strings['invalid_token']

    try:
        subprocess.run(["systemctl", "restart", service], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return strings['success']
    except Exception as e:
        return responses.PlainTextResponse(strings['error'].format(e), status_code=500)

@app.get("/uptime")
def uptime(token: str, service: str):
    if not validate_token(token):
        return strings['invalid_token']

    try:
        main_process = subprocess.Popen(['ps', '-eo', 'pid,etime'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        grep_process = subprocess.Popen(['grep', _get_unit_pid(service)], stdin=main_process.stdout,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if not grep_process.stdout:
            return {
                'status': 'fail',
                'result': 'Service is offline',
                'stdout': grep_process.stdout,
                'stderr': grep_process.stderr,
            }
        return grep_process.stdout

    except Exception as e:
        return responses.PlainTextResponse(strings['error'].format(e), status_code=500)


@app.get("/resources")
def resources(token: str, service: str):
    if not validate_token(token):
        return strings['invalid_token']

    try:
        pid = _get_unit_pid(service)
        ram = human_readable_size(
            int(
                subprocess.run(
                    [
                        "ps",
                        "--ppid",
                        pid,
                        "-o",
                        "rss",
                    ],
                    check=False,
                    stdout=subprocess.PIPE,
                )
                .stdout.decode()
                .strip()
                .split("\n")[1]
            )
            * 1024
        )

        cpu = (
                subprocess.run(
                    [
                        "ps",
                        "--ppid",
                        pid,
                        "-o",
                        r"%cpu",
                    ],
                    check=False,
                    stdout=subprocess.PIPE,
                )
                .stdout.decode()
                .strip()
                .split("\n")[1]
                + "%"
        )

        return {"status": "success",
                "cpu": cpu,
                "ram": ram}

    except Exception as e:
        return responses.PlainTextResponse(strings['error'].format(e), status_code=500)
