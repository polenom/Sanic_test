from sanic import Sanic
from sanic.response import text, json, Request, HTTPResponse
from sanic_jwt_extended import JWT, refresh_jwt_required, jwt_required
from sanic_jwt_extended.tokens import Token
from tortoise.contrib.sanic import register_tortoise
from tortoise.exceptions import DoesNotExist

from app.CRUD.view import ProductsView
from app.decorators import is_admin
from app.models import User, Products, Bill, CheckUser
from app.payment import payment
from app.serializer import  BillSerializer, TransactionSerializer, UserSerializer
from app.utils import *
from dotenv import load_dotenv


app = Sanic("My_app")
app.add_route(ProductsView.as_view(), '/products/')
app.add_route(payment, '/payment/webhook', methods=["POST"])
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


@app.middleware('response')
async def custom_banner(request: Request, response: HTTPResponse):
    response.headers['content-type'] = "application/json"

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
    urlrow = await CheckUser.filter(url=key)
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


# @app.route("/products/", methods=["GET"])
# async def products(request: Request):
#     products = await Products.all()
#     serializer = ProductsSerializer(products)
#     productsJSON = serializer.get_json()
#     return json({
#         'products': productsJSON,
#         'error': False
#     }, status=200)


@app.route("/user/bill/", methods=["GET"])
@jwt_required
@is_admin
async def get_bill(request: Request, token: Token):
    user = await User.get(name=token.identity)
    bills = await user.bill.all()
    serializer = BillSerializer(bills)
    return json({
        "error": False,
        "bills": serializer.get_json()
    })


@app.route("/user/transaction/", methods=["GET"])
@jwt_required
async def get_transaction(request: Request, token: Token):
    user = await User.get(name=token.identity)
    transactions = await  user.transaction.all()
    serializer = TransactionSerializer(transactions)
    return json({
        "error": False,
        "transactions": serializer.get_json()
    })


@app.route("/product/get/", methods=["POST"])
@jwt_required
async def buy_product(request: Request, token: Token):
    productId = request.json.get('idproduct')
    idbill = request.json.get('idbill')
    if not productId or not idbill:
        return json(error_response("Miss parameters"), status=400)
    user = await User.get(name=token.identity)
    product = await Products.filter(id=int(productId))
    bill = await Bill.filter(idBill=idbill)
    if not product:
        return json(error_response("Product does not exist"))
    if user.id != bill[0].user_id and bill[0].balance < product[0].cost:
        return json(error_response("Insufficient funds"))
    bill[0].balance = bill[0].balance - product[0].cost
    await bill[0].save()
    return json({
        'error': False
    }, status=200)


@app.route("/admin/users/", methods=["GET"])
@jwt_required
@is_admin
async def get_all_users_bill(request: Request, token: Token):
    users = await User.all()
    serializer = UserSerializer(users)
    return json({
        "error": False,
        "users": serializer.get_json()
    }, status=200)


@app.route("/admin/user/<username>", methods=["GET"])
@jwt_required
@is_admin
async def get_bill_tran_user(request: Request, token: Token, username: str):
    user = await User.filter(name=username)
    if not user:
        return json(error_response("User does not exist"), status=400)
    bill = await user[0].bill.all()
    tran = await user[0].transaction.all()
    gerbil = BillSerializer(bill)
    setraw = TransactionSerializer(tran)
    return json({
        "error": False,
        "date": { "username": username,
                  "bill": gerbil.get_json(),
                  "transaction": setraw.get_json()
        }
    })


@app.route("/admin/user/enadis/", methods=["PATCH", "PUT"])
@jwt_required
@is_admin
async def enabled_disabled_user(request: Request, token: Token):
    username = request.json.get("username")
    enabled = request.json.get("enabled")
    user = await User.filter(name=username)
    if not user:
        return json(error_response("User does not exist"), status=400)
    if user[0].isEnabled != enabled:
        user[0].isEnabled = enabled
        await user[0].save()
    return json({
        "error": False,
        "data": {"username": username,
                 "enabled": enabled}
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
