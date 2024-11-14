import contextlib
import subprocess

import psutil
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
    'error': 'Internal Server Error: {}',
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


def _find_uptime(pid: int | str) -> str:
    out = subprocess.run(['ps', '-eo', 'pid,etime'], stdout=subprocess.PIPE).stdout.decode().splitlines()

    for line in out:
        if line.split()[0] == str(pid):
            out = line
            break

    out = out.split()[1].strip()
    return out

@app.get("/")
def home_page():
    return responses.RedirectResponse(url="/docs")

@app.get("/status")
def status(token: str, service: str):
    if not validate_token(token):
        return responses.PlainTextResponse('Invalid token', status_code=401)

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
        return responses.PlainTextResponse('Invalid token', status_code=401)

    try:
        subprocess.run(["systemctl", "start", service], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return strings['success']
    except Exception as e:
        return responses.PlainTextResponse(strings['error'].format(e), status_code=500)

@app.get("/stop")
def stop(token: str, service: str):
    if not validate_token(token):
        return responses.PlainTextResponse('Invalid token', status_code=401)

    try:
        subprocess.run(["systemctl", "stop", service], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return strings['success']
    except Exception as e:
        return responses.PlainTextResponse(strings['error'].format(e), status_code=500)


@app.get("/restart")
def restart(token: str, service: str):
    if not validate_token(token):
        return responses.PlainTextResponse('Invalid token', status_code=401)

    try:
        subprocess.run(["systemctl", "restart", service], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return strings['success']
    except Exception as e:
        return responses.PlainTextResponse(strings['error'].format(e), status_code=500)

@app.get("/uptime")
def uptime(token: str, service: str):
    if not validate_token(token):
        return responses.PlainTextResponse('Invalid token', status_code=401)

    try:
        time = _find_uptime(_get_unit_pid(service))
        if not time:
            return {
                'status': 'fail',
                'result': 'Service is offline',
            }
        return {
            'status': 'success',
            'result': time,
        }

    except Exception as e:
        return responses.PlainTextResponse(strings['error'].format(e), status_code=500)


@app.get("/resources")
def resources(token: str, service: str):
    if not validate_token(token):
        return responses.PlainTextResponse('Invalid token', status_code=401)

    def _bytes_to_megabytes(b: int) -> int:
        return round(b / 1024 / 1024, 1)

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
        inf = {
            'cpu': 'n/a',
            'ram_load_mb': 'n/a',
        }
        with contextlib.suppress(Exception):
            inf["cpu"] = psutil.cpu_count(logical=True)

        with contextlib.suppress(Exception):
            inf["ram_load_mb"] = human_readable_size(psutil.virtual_memory().total)


        return {"status": "success",
                "cpu": cpu,
                "ram": ram,
                "cpu_total": inf['cpu'],
                "ram_total": inf['ram_load_mb'],
        }

    except Exception as e:
        return responses.PlainTextResponse(strings['error'].format(e), status_code=500)
