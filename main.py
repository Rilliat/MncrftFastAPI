import requests


def testing():
    url = "http://127.0.0.1:8000/get_status?token=testtoken&service=rilxiaoserver"
    response = requests.get(url)
    return response.json()


result = testing()
for i in result:
    print(i)