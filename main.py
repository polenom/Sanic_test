import datetime
import os
import json as JSON

from sanic import Sanic
from sanic.response import text, json, Request
from sanic_jwt import Initialize, protected
from sanic_jwt_extended import JWT, refresh_jwt_required, jwt_required
from sanic_jwt_extended.tokens import Token
from tortoise.contrib.sanic import register_tortoise
from tortoise.exceptions import DoesNotExist

from app.models import User, Products, Bill, CheckUser
from app.serializer import ProductsSerializer
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
@app.route("/user/create/", methods=['POST'])
async def create_user(request):
    username = request.json.get("username")
    password = request.json.get("password")
    email = request.json.get("email")
    if not username or not password or not email:
        return json(error_response("Missing username or password or email"), status=400)
    if await User.filter(name=username):
        return json(error_response("There is user with this name"), status=400)
    user = User(
        name=username,
        password=get_pass(password),
        email=email
    )
    await user.save()
    key = create_key(user.name)
    await CheckUser(
        user=user,
        url=key
    ).save()
    return json({"link": create_link(key),
                 "error": False
                 })


@app.route("/user/checklink/<key>", methods=["GET"])
async def check_link(request: Request, key: str):
    urlrow = await CheckUser.filter(url = key)
    if not urlrow:
        return json(error_response("Link does not exist"), status=400)
    user = await urlrow[0].user
    user.isCheckUser = True
    await user.save()
    await urlrow[0].delete()
    return json({
        "error": False,
        "message": "User verified"
    }, status=200)


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


@app.route("/products/", methods=["GET"])
async def products(request: Request):
    products = await Products.all()
    serializer = ProductsSerializer(products)
    productsJSON = serializer.get_json()
    return json({
        'products': productsJSON,
        'error': False
    }, status=200)



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
