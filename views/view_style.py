import os
from flask import request, abort, make_response
from flask_cors import CORS, cross_origin
from app import app
from models import Merchant, MerchantSettings


@app.route('/ecocart.css')
@cross_origin()
def style_css():
    shop_name = request.args.get('shop_name')

    if not shop_name:
        abort(403)

    try:
        merchant = Merchant.get(Merchant.shop_name == shop_name)
        merchant_settings = MerchantSettings.get(MerchantSettings.merchant == merchant)

    except Merchant.DoesNotExist:
        app.logger.warning('not merchant')
        abort(403)

    if not merchant.enable:
        app.logger.warning('merchant disable')
        abort(403)

    data = ''

    if merchant_settings.default_view:
        html_path = app.config.get('DEFAULT_SETTINGS_HTML_PATH')

        with open(os.path.join(html_path, 'style.css')) as f:
            data = f.read()

    else:
        data = merchant_settings.style

    response = make_response(data)
    response.headers['Content-Type'] = 'text/css'

    return response
