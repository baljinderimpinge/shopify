import os
from flask import request, abort, make_response
from flask_cors import CORS, cross_origin
from app import app
from models import Merchant, MerchantSettings


def save_default_html(merchant):
    # запишем дефолтные экокарт html/стили
    try:
        merchant_settings = MerchantSettings.get(MerchantSettings.merchant == merchant)

    except MerchantSettings.DoesNotExist:
        merchant_settings = MerchantSettings()
        merchant_settings.merchant = merchant

    html_path = app.config.get('DEFAULT_SETTINGS_HTML_PATH')

    with open(os.path.join(html_path, 'loading.html')) as f:
        merchant_settings.loading = f.read()

    with open(os.path.join(html_path, 'estimate.html')) as f:
        merchant_settings.estimate = f.read()

    with open(os.path.join(html_path, 'shipment.html')) as f:
        merchant_settings.shipment = f.read()

    with open(os.path.join(html_path, 'error.html')) as f:
        merchant_settings.error_field = f.read()

    with open(os.path.join(html_path, 'style.css')) as f:
        merchant_settings.style = f.read()

    merchant_settings.default_view = True
    merchant_settings.save()


@app.route('/reset')
@cross_origin()
def reset_view():
    shop_name = request.args.get('shop_name')

    if not shop_name:
        abort(403)

    try:
        merchant = Merchant.get(Merchant.shop_name == shop_name)
        save_default_html(merchant)

    except Merchant.DoesNotExist:
        app.logger.warning('not merchant')
        abort(403)

    if not merchant.enable:
        app.logger.warning('merchant disable')
        abort(403)

    return 'ok'
