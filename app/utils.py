import datetime
import hashlib
import os

from dotenv import load_dotenv
from sanic_jwt_extended import JWT

load_dotenv()
SALT = os.getenv("SALT")
SALT_LINK = os.getenv("SALT_LINK")


def get_pass(password: str, salt: str = SALT) -> str | None:
    if password:
        return hashlib.sha512((salt + password).encode()).hexdigest()


def error_response(msg: str) -> dict:
    return dict(
        error=True,
        message=msg
    )


def get_access_and_refresh_tokens(identity: str) -> tuple[str]:
    access_token = get_access_token(identity)
    refresh_token = get_refresh_token(identity)
    return (access_token, refresh_token)


def get_access_token(identity: str) -> str:
    return JWT.create_access_token(
        identity=identity,
        expires_delta=datetime.timedelta(minutes=5)
    )


def get_refresh_token(identity: str) -> str:
    return JWT.create_refresh_token(
        identity=identity,
        expires_delta=datetime.timedelta(days=1),
    )


def create_key(name: str) -> str:
    return hashlib.md5((SALT_LINK + name).encode()).hexdigest()

def create_link(key: str) -> str:
    url = "http://127.0.0.1:8000/user/checklink/"
    return  url + key

