from app.models import Products


class ProductsSerializer():
    def __init__(self, products: list):
        self.products = products

    def get_json(self) -> list[dict]:
        result = []
        for elem in self.products:
            result.append(self.obj_to_dict(elem))
        return result

    def obj_to_dict(self, elem: Products ) -> dict:
        return {
            'id': elem.pk,
            'title': elem.title,
            'description': elem.description,
            'cost': elem.cost
        }