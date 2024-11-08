import requests


def testing():
    url = "http://95.79.26.24:8123/get_status?token=testtoken&service=rilxiaoserver"
    response = requests.get(url)
    return response.json()


result = testing()
for i in result:
    print(i)