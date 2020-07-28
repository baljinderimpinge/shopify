import datetime
from peewee import CharField, DateTimeField, TextField, BooleanField, \
    ForeignKeyField, DecimalField, IntegerField, FloatField

from app import db_wrapper


class Merchant(db_wrapper.Model):
    shop_name = CharField(70, unique=True)
    token = CharField(50, null=True)
    created = DateTimeField(default=datetime.datetime.utcnow, null=True)  # время создания в юникоде
    settings = TextField(null=True)  # закодированный json обьект
    enable = BooleanField(default=False, null=True)


class Shopify_Order(db_wrapper.Model):
    merchant = ForeignKeyField(Merchant, null=True, on_delete='CASCADE')
    created = DateTimeField(default=datetime.datetime.utcnow, null=True,
                            index=True)  # время создания в юникоде
    order_id = CharField(null=True, index=True)
    order_sum = DecimalField(15, 2, null=True)
    order_eco_sum = DecimalField(15, 2, null=True)
    economy_co2 = DecimalField(15, 2, null=True)
    currency = CharField(3, null=True)
    sent = BooleanField(default=False, null=True)
    fee = IntegerField(null=True)


class Shopify_Order_Data(db_wrapper.Model):
    shopify_order = ForeignKeyField(Shopify_Order, null=True, on_delete='CASCADE', unique=True)
    data = TextField(null=True)


class Ecocart_Product(db_wrapper.Model):
    merchant = ForeignKeyField(Merchant, null=True, on_delete='CASCADE')
    shopify_product_id = CharField(null=True)
    last_variant = IntegerField(null=True)


class MerchantSettings(db_wrapper.Model):
    merchant = ForeignKeyField(Merchant, null=True, on_delete='CASCADE', unique=True)
    selector = CharField(null=True)
    placement = CharField(null=True)
    selector_method = CharField(null=True)
    js = TextField(null=True)
    default_view = BooleanField(default=True)
    style = TextField(null=True)
    estimate = TextField(null=True)
    shipment = TextField(null=True)
    loading = TextField(null=True)
    error_field = TextField(null=True)
    company = CharField(null=True)
    url_dashboard = CharField(null=True)
