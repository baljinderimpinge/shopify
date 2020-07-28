from flask import request, redirect
import shopify
from flask_cors import CORS, cross_origin
from app import app


@app.route('/authorize')
@cross_origin()
def authorize():
    """авторизация приложения"""
    shop_name = request.args.get('shop')
    shopify.Session.setup(api_key=app.config['SHOPIFY_API_KEY'],
                          secret=app.config['SHOPIFY_API_SECRET'])

    session = shopify.Session(shop_name, app.config.get('SHOPIFY_API_VERSION'))
    scope = app.config.get('SCOPE')
    redirect_url = 'https://{}/finalize'.format(app.config.get('HOSTNAME'))
    permission_url = session.create_permission_url(scope, redirect_url)

    return redirect(permission_url)
