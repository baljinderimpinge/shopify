import json

import requests
from flask import request, jsonify, abort
from flask_cors import CORS, cross_origin
from lib.functions import calc_ecocart, get_ecocart_variant, \
    get_location_address, Ecocart, clear_cart
from app import app
from models import Merchant


@app.route('/ecocart')
@cross_origin()
def ecocart():
    shop_name = request.args.get('shop_name')
    shipping_weight = float(request.args.get('total_weight', 0)) # граммы
    if not shop_name or not shipping_weight:
        abort(403)
    shipping_weight = shipping_weight / 1000 * 2.205
    shipping_weight = round(shipping_weight, 4) # подогнать под количество знаков shopify
    try:
        merchant = Merchant.get(Merchant.shop_name == shop_name)
        token = merchant.token
        print(token)
    except Merchant.DoesNotExist:
        app.logger.warning('not merchant')
        abort(403)




    remote_ip = request.headers.get('X-Real-IP')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    shipping_po = None
    if latitude and longitude:
        shipping_po = (float(latitude), float(longitude))
    path_geo_db = app.config.get('PATH_GEO_DB')
    path_geo_db_us = app.config.get('PATH_GEO_DB_US')
    _kwargs = dict(
        shipping_weight=shipping_weight,
        ip_address=remote_ip,
        shipping_po=shipping_po,
        path_db=path_geo_db,
        path_db_us=path_geo_db_us
    )
    print(_kwargs)
    shopify_location_address = get_location_address(shop_name, token)
    _kwargs.update({'shopify_location_address': shopify_location_address})
    calc_amount = calc_ecocart(**_kwargs)
    app.logger.warning('calc_amount {}'.format(calc_amount))
    variant_id = get_ecocart_variant(merchant, shipping_weight, calc_amount)

    return jsonify({'calc': calc_amount, 'variant_id': variant_id})


# LIVE
@app.route('/ecocart', methods=['POST'])
@cross_origin()
def ecocart2():
    shop_name = request.form.get('shop_name')
    cart = request.form.get('cart')

    if not shop_name or not cart:
        abort(403)
    cart = json.loads(cart)
    try:
        merchant = Merchant.get(Merchant.shop_name == shop_name)
        token = merchant.token
        print(token)

    except Merchant.DoesNotExist:
        app.logger.warning('not merchant')
        abort(403)

    if not merchant.enable:
        abort(403)

    # проверить экопродукт, установить если удален
    image_url = app.config.get('ECOCART_IMAGE_URL')
    e = Ecocart(image_url, merchant, shop_name)
    shopify_product_id = e.install()

    cart, cart_clear = clear_cart(cart, shopify_product_id)
    shipping_weight = float(cart.get('total_weight', 0))  # граммы
    shipping_weight = shipping_weight * 0.002205
    shipping_weight = round(shipping_weight,
                            1)  # подогнать под количество знаков shopify
    remote_ip = request.headers.get('X-Real-IP')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    shipping_po = None
    if latitude and longitude:
        shipping_po = (float(latitude), float(longitude))
    path_geo_db = app.config.get('PATH_GEO_DB')
    path_geo_db_us = app.config.get('PATH_GEO_DB_US')

    try:
        settings = json.loads(merchant.settings)
        default_weight = settings.get('default_weight')

        print('default_weight')
        print(default_weight)

        with open(app.config.get('ECOCART_SETTINGS_PATH')) as f:
            ecocart_settings = json.load(f)

        product_types = ecocart_settings.get('product_types')
        offset_shipping_cost = ecocart_settings.get('offset_shipping_cost')
        offset_manufacturing_cost = ecocart_settings.get('offset_manufacturing_cost')
        fee = ecocart_settings.get('fee')
        secondary_product_types = ecocart_settings.get('secondary_product_types')
        tons_of_co2_offset_variable = ecocart_settings.get('tons_of_co2_offset_variable')

    except:
        print('x')
        abort(403)

    if not settings.get('production'):
        print('prod')
        abort(403)

    _kwargs = dict(
        cart=cart,
        ip_address=remote_ip,
        shipping_po=shipping_po,
        path_db=path_geo_db,
        path_db_us=path_geo_db_us,
        default_weight=default_weight,
        product_types=product_types,
        offset_shipping_const=offset_shipping_cost,
        offset_manufacturing_cost=offset_manufacturing_cost,
        fee=fee,
        primary_product_types=settings.get('product_types'),
        default_shipping_distance=ecocart_settings.get('default_shipping_distance'),
        secondary_product_types=secondary_product_types
    )
    print(_kwargs)
    shopify_location_address = get_location_address(shop_name, token)
    print('*' )
    print(shopify_location_address)
    _kwargs.update({'shopify_location_address': shopify_location_address})

    # тип расчета
    calc_amount, ecocart_calc = calc_ecocart(**_kwargs)

    app.logger.warning('calc_amount {}'.format(calc_amount))

    # co 2
    co2 = ((calc_amount - 0.15) * tons_of_co2_offset_variable) * 2205
    co2 = round(co2, 2)
    shipping_weight = co2

    if calc_amount:
        variant_id = get_ecocart_variant(merchant, shipping_weight, calc_amount)
        calc_amount = '{:.2f}'.format(calc_amount)

    else:
        variant_id = None

    # для компани еще 1 плашку

    return jsonify({'calc': calc_amount, 'variant_id': variant_id,
                    'fee': settings.get('fee'), 'run_result': ecocart_calc.run_result})
