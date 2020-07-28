from collections import OrderedDict
import hashlib
import hmac


def signature_validation(params, api_secret):
    """
    проверка подписи входящих get параметров
    :param params: request.args.items()
    :param api_secret: API secret key (app info) вашего public app с акаунта partner
    :return: bool
    """
    sorder_params = OrderedDict(sorted(params, key=lambda t: t[0]))
    hmac_param = sorder_params.pop('hmac')
    sorder_params = ['{}={}'.format(k, sorder_params[k]) for k in sorder_params]
    sorder_params = '&'.join(sorder_params)
    h = hmac.new(api_secret.encode('utf-8'), msg=sorder_params.encode('utf-8'),
                 digestmod=hashlib.sha256).hexdigest()

    return hmac.compare_digest(hmac_param, h)


def signature_validation_with_ids(params, api_secret):
    """
    проверка подписи входящих get параметров c ids параметрами
    :param params: FLASK request.args.items(multi=True) для выборки одинаковых ключей
    :param api_secret: API secret key (app info) вашего public app с акаунта partner
    :return: bool
    """
    # достаем ids
    ids = []
    temp_params = []

    for param in params:

        if param[0] == 'ids[]':
            ids.append(param[1])

        else:
            temp_params.append(param)

    if ids:
        params = temp_params
        ids = ['"{}"'.format(str(row)) for row in ids]
        ids = ', '.join(ids)
        ids = '[' + ids + ']'
        params.append(('ids', ids))

    sorted_params = OrderedDict(sorted(params, key=lambda t: t[0]))
    hmac_param = sorted_params.pop('hmac')
    sorted_params = ['{}={}'.format(k, sorted_params[k]) for k in sorted_params]
    sorted_params = '&'.join(sorted_params)
    h = hmac.new(api_secret.encode('utf-8'), msg=sorted_params.encode('utf-8'),
                 digestmod=hashlib.sha256).hexdigest()

    return hmac.compare_digest(hmac_param, h)
