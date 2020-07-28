import json
from flask import request, abort, render_template
from flask_cors import CORS, cross_origin
from app import app
from models import Merchant, MerchantSettings


@app.route('/ecocart.js')
@cross_origin()
def ecocart_js():
    shop_name = request.args.get('shop_name')

    if not shop_name:
        abort(403)

    try:
        merchant = Merchant.get(Merchant.shop_name == shop_name)
        merchant_settings = MerchantSettings.get(MerchantSettings.merchant == merchant)

    except Merchant.DoesNotExist:
        app.logger.warning('not merchant')
        abort(403)

    except MerchantSettings.DoesNotExist:
        app.logger.warning('not merchant_settings')
        abort(403)

    if not merchant.enable:
        app.logger.warning('merchant disable')
        abort(403)

    settings = merchant.settings

    if settings:
        settings = json.loads(settings)

    else:
        settings = dict()

    if not settings.get('production'):
        app.logger.warning('production disable')
        abort(403)

    selector = merchant_settings.selector

    if not selector:
        selector = '';

    placement = merchant_settings.placement
    js = merchant_settings.js or ''
    hostname = app.config.get('HOSTNAME')

    return render_template('ecocart.js', selector=selector, placement=placement,
                           js=js, hostname=hostname)
