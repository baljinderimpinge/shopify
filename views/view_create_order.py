import json
from decimal import Decimal
from flask import request, abort
import shopify
from flask_cors import CORS, cross_origin
from lib.verify_webhook import verify
from app import app
from models import Merchant, Shopify_Order, Shopify_Order_Data, Ecocart_Product


@app.route('/create_order/<shop_short>', methods=['POST'])
@cross_origin()
def create_order_view(shop_short):
    """Обработчик вебхука создания ордера
    :param shop_short:
    :return:
    """
    if not verify(request.get_data(),
                  request.headers.get('X-Shopify-Hmac-Sha256'),
                  app.config.get('SHOPIFY_API_SECRET')):
        app.logger.warning('bad sign')
        abort(403)

    if not request.is_json:
        app.logger.warning('not json')
        abort(403)

    order = request.get_json()
    shop_name = request.headers.get('X-Shopify-Shop-Domain')
    order_id = int(request.headers.get('X-Shopify-Order-Id'))

    try:
        merchant = Merchant.get(Merchant.shop_name == shop_name)

    except Merchant.DoesNotExist:
        abort(404)

    try:
        settings = json.loads(merchant.settings)
        fee = int(settings.get('fee'))

    except:
        app.logger.warning('fee = None')
        fee = None

    ecocart_product = Ecocart_Product.get(Ecocart_Product.merchant == merchant)
    product_id = ecocart_product.shopify_product_id
    order_eco_sum = None

    for item in order.get('line_items'):

        if str(item.get('product_id')) != product_id:
            continue

        order_eco_sum = Decimal(item.get('price'))

    shopify_order = Shopify_Order()
    shopify_order.merchant = merchant
    shopify_order.order_id = order_id

    if order_eco_sum:
        shopify_order.order_eco_sum = order_eco_sum

    shopify_order.currency = order.get('currency')
    shopify_order.order_sum = Decimal(order.get('total_price'))
    shopify_order.fee = fee
    shopify_order.save()
    shopify_order_data = Shopify_Order_Data()
    shopify_order_data.shopify_order = shopify_order
    shopify_order_data.data = json.dumps(order, ensure_ascii=False)
    shopify_order_data.save()

    return ''
