import os

from sanic import Sanic
from sanic.response import text, json
from sanic_jwt import Initialize
from tortoise.contrib.sanic import register_tortoise

from app.models import User, Products, Bill
from app.permission import authenticate
from app.utils import getPass
from dotenv import load_dotenv

load_dotenv()
app = Sanic("My_app")
register_tortoise(app, db_url="postgres://sanic:sanic@0.0.0.0:2020/sanicproject", modules={"models": ["app.models"]},
                  generate_schemas=True)
Initialize(
    app,
    authenticate=authenticate,
    access_token_name="token",
    url_prefix='/user/auth',
    secret=os.getenv('TOKEN'))
SALT = os.getenv("SALT")

@app.get("/")
async def hello_world(request):
    print(request)
    return text("hello world")


@app.post("user/create/<user>")
async def create_user(request, user):
    # await User(
    # name = "admin",
    # password = getPass('admin')
    # ).save()
    a = await User.filter(id=1)
    print(type(a[0]))
    # await Bill(
    #     user = a[0],
    #     idBill = "123131k3j21jjdlsjfl12312",
    #     balance = 13 ).save()
    print(type(request))
    return json({"user": "admin",
                 "error": False
                 })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
