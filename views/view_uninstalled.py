import requests

from flask import request, abort
from flask_cors import CORS, cross_origin
from lib.verify_webhook import verify
from app import app
from models import Merchant


@app.route('/uninstalled', methods=['POST'])
@cross_origin()
def uninstalled_view():
    """Обработчик вебхука удаления аппа
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

    shop_name = request.headers.get('X-Shopify-Shop-Domain')

    try:
        merchant = Merchant.get(Merchant.shop_name == shop_name)

    except Merchant.DoesNotExist:
        abort(404)

    try:
        _ = requests.get(app.config.get('DELETE_APP_URL').format(merchant.id),
                         timeout=30)

    except:
        app.logger.warning('DELETE_APP_URL exception')

    return ''
