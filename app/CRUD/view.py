from sanic.response import Request, json
from sanic.views import HTTPMethodView
from sanic_jwt_extended import jwt_required
from sanic_jwt_extended.tokens import Token

from app.decorators import is_admin
from app.models import Products
from app.serializer import ProductsSerializer
from app.utils import error_response


class ProductsView(HTTPMethodView):
    async def get(self, request: Request):
        products = await Products.all()
        serializer = ProductsSerializer(products)
        productsJSON = serializer.get_json()
        return json({
            'products': productsJSON,
            'error': False
        }, status=200)


    @jwt_required
    @is_admin
    async def post(self, request: Request, token: Token):
        title = request.json.get('title')
        description = request.json.get('description')
        cost = request.json.get('cost')
        if not title or not description or not cost:
            return json(error_response("Not all fields"), status=400)
        await Products(
            title=title,
            description=description,
            cost=float(cost)
        ).save()
        return json({
            "error": False,
            "date": {
                "title": title,
                "description": description,
                "cost": cost
            }
        })

    @jwt_required
    @is_admin
    async def put(self, request: Request, token: Token):
        id = request.json.get('id')
        title = request.json.get('title')
        description = request.json.get('description')
        cost = request.json.get('cost')

        if not id:
            return json(error_response("Not id"), status=400)
        product = await Products.filter(pk=int(id))
        if not product:
            return json(error_response("Not products"), status=400)
        product[0].title = title if title else product[0].title
        product[0].description = description if description else product[0].title
        product[0].cost = cost if cost else product[0].title
        await product[0].save()
        return json({
            "error": False,
            "date": {
                "title": title,
                "description": description,
                "cost": cost
            }
        }, status=200)


    @jwt_required
    @is_admin
    async def delete(self, request: Request, token: Token):
        id = request.json.get('id')
        if not id:
            return json(error_response("Not id"), status=400)
        product = await Products.filter(pk=int(id))
        if not product:
            return json(error_response("Not products"), status=400)
        await product[0].delete()
        return json({
            "error": False,
            "result": True
        }, status=200)