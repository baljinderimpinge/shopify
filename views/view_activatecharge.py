from flask import request, redirect, abort
from flask_cors import CORS, cross_origin
from app import app
from models import Merchant
from lib.shopify_charge import run_activate_charge


@app.route('/activatecharge/<shop_name>')
@cross_origin()
def activatecharge(shop_name):
    charge_id = request.args.get('charge_id')

    try:
        merchant = Merchant.get(Merchant.shop_name == shop_name)

    except Merchant.DoesNotExist:
        abort(403)

    token = merchant.token
    run_activate_charge(shop_name, token, charge_id)
    # редирект в админку
    url = 'https://{}/admin/apps/{}'

    return redirect(url.format(shop_name, app.config.get('SHOPIFY_API_KEY')))