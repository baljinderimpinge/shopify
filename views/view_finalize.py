import os

from flask import request, redirect
import shopify
from flask_cors import CORS, cross_origin
from app import app
from lib.functions import pause_sdk
from models import Merchant, Ecocart_Product, MerchantSettings
from lib.functions import Ecocart
from lib.shopify_charge import create_application_charge


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





@app.route('/finalize')
@cross_origin()
def finalize():
    code = request.args.get('code')
    shop_name = request.args.get('shop')
    timestamp = request.args.get('timestamp')
    hmac = request.args.get('hmac')
    params = {
        'code': code,
        'timestamp': timestamp,
        'hmac': hmac,
        'shop': shop_name
    }
    api_version = app.config.get('SHOPIFY_API_VERSION')
    shopify.Session.setup(api_key=app.config['SHOPIFY_API_KEY'],
                          secret=app.config['SHOPIFY_API_SECRET'])
    session = shopify.Session(shop_name, api_version)
    token = session.request_token(params)

    try:
        merchant = Merchant.get(Merchant.shop_name == shop_name)

    except Merchant.DoesNotExist:
        merchant = Merchant()
        merchant.enable = False
        merchant.shop_name = shop_name

    merchant.token = token
    merchant.save()

    save_default_html(merchant)

    shop_short = shop_name.replace('.myshopify.com', '')

    need_webhooks = [
        {
            'url': 'https://{}/create_order/{}'.format(
                app.config.get('HOSTNAME'), shop_short),
            'topic': 'orders/create',
            'created': False
        },
        {
            'url': 'https://{}/uninstalled'.format(
                app.config.get('HOSTNAME')),
            'topic': 'app/uninstalled',
            'created': False
        },
    ]

    with shopify.Session.temp(shop_name, api_version, merchant.token):
        webhooks = shopify.Webhook.find()

        for webhook in webhooks:

            for need_webhook in need_webhooks:

                if webhook.topic == need_webhook.get('topic') and \
                        webhook.address == need_webhook.get('url'):
                    need_webhook.update({'created': True})

        for need_webhook in need_webhooks:

            if need_webhook.get('created'):
                continue

            app.logger.info('create webhook {}'.format(need_webhook.get('topic')))
            webhook = shopify.Webhook()
            webhook.topic = need_webhook.get('topic')
            webhook.address = need_webhook.get('url')
            webhook.format = 'json'
            webhook.save()
            pause_sdk(2)

        ecocart_script = shopify.ScriptTag()
        ecocart_script.event = 'onload'
        ecocart_script.src = 'https://{}/ecocart.js?shop_name={}'.format(
            app.config.get('HOSTNAME'), shop_name)
        ecocart_script.save()

    image_url = app.config.get('ECOCART_IMAGE_URL')
    e = Ecocart(image_url, merchant)
    e.install()

    if not app.config.get('CHARGE_ENABLE'):
        url = 'https://{}/admin/apps/{}'
        # редирект в админку
        return redirect(url.format(shop_name, app.config.get('SHOPIFY_API_KEY')))

    # подписка
    return_url = 'https://{}/activatecharge/{}'
    return_url = return_url.format(app.config.get('HOSTNAME'), shop_name)
    data_create = {
        'name': app.config.get('CHARGE_NAME'),
        'price': 0.5,
        'return_url': return_url,
        'test': app.config.get('CHARGE_TEST'),
    }
    url = create_application_charge(shop_name, token, data_create)

    return redirect(url)
