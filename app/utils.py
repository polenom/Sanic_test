import datetime
import hashlib
import os

from dotenv import load_dotenv
from sanic_jwt_extended import JWT

load_dotenv()
SALT = os.getenv("SALT")


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
