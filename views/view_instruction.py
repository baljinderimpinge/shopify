import urllib
import traceback
from flask_cors import CORS, cross_origin
from flask import request, render_template, abort, redirect

import shopify
import pyactiveresource

from lib.signature_validation import signature_validation
from app import app
from models import Merchant


def reinstall_app(shop_name):
    app.logger.info('reinstall app for {}'.format(shop_name))
    args = urllib.parse.urlencode({'shop': shop_name})
    url = 'https://{}/authorize?{}'
    # редирект в админку
    return redirect(url.format(app.config.get('HOSTNAME'), args))


@app.route('/instruction', methods=['GET', 'POST'])
@cross_origin()
def instruction():
    shop_name = request.args.get('shop')
    api_version = app.config.get('SHOPIFY_API_VERSION')

    if not shop_name:
        abort(403)

    try:
        # проверка подписи
        if not signature_validation(request.args.items(),
                                    app.config['SHOPIFY_API_SECRET']):
            raise Exception('bad sign')

        merchant = Merchant.get(Merchant.shop_name == shop_name)

        with shopify.Session.temp(shop_name, api_version, merchant.token):
            shop = shopify.Shop.current()
            myshopify_domain = shop.myshopify_domain
            app.logger.info(myshopify_domain)

    except Merchant.DoesNotExist:
        return reinstall_app(shop_name)

    except pyactiveresource.connection.UnauthorizedAccess:
        # если токен не активен переустановить апп
        return reinstall_app(shop_name)

    except:
        app.logger.warning(traceback.format_exc())
        abort(403)

    return render_template('instruction.html')
