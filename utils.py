import random
import string


def validate_token(token: str):
    with open('api_tokens.txt', 'r', encoding='utf-8') as file:
        return token in [line.replace('\n', '') for line in file.readlines()]


def create_token():
    with open('api_tokens.txt', 'a', encoding='utf-8') as file:
        token = ''
        for _ in range(32):
            token += random.choice(string.digits + string.ascii_lowercase + string.digits)
        file.write('\n'+token)
        return token

