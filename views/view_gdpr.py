import traceback
import json
from flask import request, abort
from flask_cors import CORS, cross_origin
from lib.verify_webhook import verify
#from lib.send_data import send_mail2

from app import app


@app.route('/cdre', methods=['POST'])
@app.route('/cdee', methods=['POST'])
@app.route('/sdre', methods=['POST'])
@cross_origin()
def gdpr_view():
    """ GDPR webhooks
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

    j = request.get_json()
    message = '{}\n\n{}'.format(request.url, json.dumps(j))
    app.logger.warning('gdpr')
    app.logger.warning(request.url)
    app.logger.warning(message)
    '''
    # пока в консоль!
    try:
        send_mail2('gdpr', message, 'dev@trademinister.de')
    except:
        app.logger.error(traceback.format_exc())

    return ''
    '''