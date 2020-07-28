import os
from flask import request, abort, jsonify
from flask_cors import CORS, cross_origin
from app import app
from models import Merchant, MerchantSettings


@app.route('/ecocart.json')
@cross_origin()
def ecocart_json():
    shop_name = request.args.get('shop_name')

    if not shop_name:
        abort(403)

    try:
        merchant = Merchant.get(Merchant.shop_name == shop_name)
        merchant_settings = MerchantSettings.get(MerchantSettings.merchant == merchant)
        company = merchant_settings.company

        if not company:
            company = '[Company]'

    except Merchant.DoesNotExist:
        app.logger.warning('not merchant')
        abort(403)

    if not merchant.enable:
        app.logger.warning('merchant disable')
        abort(403)

    html_path = app.config.get('DEFAULT_SETTINGS_HTML_PATH')
    data = dict()

    if merchant_settings.default_view:

        with open(os.path.join(html_path, 'loading.html')) as f:
            data['loading'] = f.read()

        with open(os.path.join(html_path, 'estimate.html')) as f:
            data['estimate'] = f.read()

        with open(os.path.join(html_path, 'shipment.html')) as f:
            data['shipment'] = f.read()

        with open(os.path.join(html_path, 'error.html')) as f:
            data['error'] = f.read()

    else:
        data['loading'] = merchant_settings.loading
        data['estimate'] = merchant_settings.estimate
        data['shipment'] = merchant_settings.shipment
        data['error'] = merchant_settings.error_field

    with open(os.path.join(html_path, 'company.html')) as f:
        data['company'] = f.read()
        data['company'] = data['company'].replace('##COMPANY##', company)

    return jsonify(data)
