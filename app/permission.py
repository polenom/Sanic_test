from typing import Type, Union

from sanic.response import Request
from sanic_jwt import exceptions

from app.models import User


async def authenticate(request: Type[Request], *args, **kwargs) -> Type[Union[User,
                                                                              exceptions.AuthenticationFailed,]] :
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if not username or not password:
        raise exceptions.AuthenticationFailed("Missing username or password.")
    print(username, password)
    user = await User.filter(name=username)
    print(user,321)
    if not user:
        raise exceptions.AuthenticationFailed('User not found')
    print(user,123)
    return user[0]
