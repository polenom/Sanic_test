from tortoise.models import Model
from tortoise import fields


class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(unique=True,max_length=50)
    email = fields.CharField(null=True, max_length=50)
    password = fields.CharField(200)
    isAdmin = fields.BooleanField(default=False)
    isCheckUser = fields.BooleanField(default=False)
    isEnabled = fields.BooleanField(default=False)

    def to_dict(self):
        return {"user_id": self.id, "username": self.name}

    def __str__(self):
        return str(self.name)


class CheckUser(Model):
    user = fields.OneToOneField('models.User', related_name="checkuser", on_delete="CASCADE")
    url = fields.TextField(50)


class Products(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(50)
    description = fields.CharField(200)
    cost = fields.FloatField()

    def __str__(self):
        return str(self.name)


class Bill(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='bill', on_delete="CASCADE")
    idBill = fields.CharField(150)
    balance = fields.FloatField()


class Transaction(Model):
    id = fields.SmallIntField(pk=True)
    bill = fields.ForeignKeyField('models.Bill', related_name='transaction', on_delete="CASCADE")
    idTran = fields.IntField()
    amount = fields.FloatField()


