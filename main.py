import datetime
import os
import json as JSON

from sanic import Sanic
from sanic.response import text, json, Request
from sanic_jwt import Initialize, protected
from sanic_jwt_extended import JWT, refresh_jwt_required, jwt_required
from sanic_jwt_extended.tokens import Token
from tortoise.contrib.sanic import register_tortoise

from app.models import User, Products, Bill
from app.utils import *
from dotenv import load_dotenv

app = Sanic("My_app")
load_dotenv()
register_tortoise(app, db_url="postgres://sanic:sanic@0.0.0.0:2020/sanicproject", modules={"models": ["app.models"]},
                  generate_schemas=True)

with JWT.initialize(app) as manager:
    manager.config.secret_key = os.getenv("TOKEN")



@app.get("/")
@jwt_required
async def hello_world(request: Request, token: Token):
    print(request)
    return text("hello world")
#
#
@app.post("/user/create/")
async def create_user(request):
    await User(
    name = "admin",
    password = get_pass('admin')
    ).save()
    return json({"user": "admin",
                 "error": False
                 })

@app.route("/login", methods=["POST"])
async def login(request: Request):
    username = request.json.get("username")
    password = request.json.get("password")
    if not username or not password:
        return json(error_response("Missing username or password"),
                    status=400)
    user = await User.filter(name=username)
    if not user:
        return json(error_response("User not found"),
                    status=400)
    if user[0].password != get_pass(password):
        return json(error_response("Password error"),
                    status=400)
    access_token, refresh_token = get_access_and_refresh_tokens(user[0].name)
    return json(
        dict(
            access_token=access_token,
            refresh_token=refresh_token
        ),
        status=200
    )


@app.route("/refresh", methods=['POST'])
@refresh_jwt_required
async def refresh(request: Request, token: Token):
    access_token, refresh_token = get_access_and_refresh_tokens(token.identity)
    return json(
        dict(
            access_token=access_token,
            refresh_token=refresh_token
        ),
        status=200
    )



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
