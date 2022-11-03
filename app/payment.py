import hashlib
import os

from sanic.response import Request, json
from dotenv import load_dotenv

from app.models import User, Transaction

load_dotenv()


async def payment(request: Request):
    signature = request.json.get("signature")
    transaction_id = request.json.get("transaction_id")
    user_id = request.json.get("user_id")
    bill_id = request.json.get("bild_id")
    amount = request.json.get("amount")
    signa= f"{os.getenv('PRIVET_KEY')}:{transaction_id}:{user_id}:{bill_id}:{amount}".encode()
    if hashlib.sha1(signa).hexdigest() != signature:
        return json({
            "result": False
        }, status=400)
    user = await User.filter(pk=user_id)
    bill = await user.bill.get(idBill=bill_id)
    await Transaction(
        user=user,
        idTran=transaction_id,
        amount=amount
    ).save()
    bill.balance += amount
    await bill.save()
    return json({
        "result": True
    }, status=False)
