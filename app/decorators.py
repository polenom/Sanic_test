from functools import wraps

from sanic import json

from app.models import User


def is_admin(function):
    def decorator(f, *args, **kwargs):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            user = await User.get(name=kwargs["token"].identity)
            if user.isAdmin:
                return await f(request, *args, **kwargs)
            return json({
                "error": True,
                "message": "User is not admin"
            })

        return decorated_function

    return decorator(function)
