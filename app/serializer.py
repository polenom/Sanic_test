from app.models import Products, Bill, Transaction


class ProductsSerializer():
    def __init__(self, elems: list):
        self.elems = elems

    def get_json(self) -> list[dict]:
        result = []
        for elem in self.elems:
            result.append(self.obj_to_dict(elem))
        return result

    def obj_to_dict(self, elem: Products ) -> dict:
        return {
            'id': elem.pk,
            'title': elem.title,
            'description': elem.description,
            'cost': elem.cost
        }


class BillSerializer(ProductsSerializer):
    def obj_to_dict(self, elem: Bill ) -> dict:
        return {
            'id': elem.pk,
            "idBill": elem.idBill,
            "balance": elem.balance
        }


class TransactionSerializer(ProductsSerializer):

    def obj_to_dict(self, elem: Transaction ) -> dict:
        return {
            "id": elem.id,
            "idTransaction": elem.idTran,
            "amount": elem.amount
        }