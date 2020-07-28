import logging
import traceback
import requests


class ChargeExc(Exception):
    pass


# единовременная оплата
def create_application_charge(shop_name, token, data):
    data = {
        'application_charge': data
    }
    headers = {'X-Shopify-Access-Token': token}
    url = 'https://{}/admin/api/2020-01/application_charges.json'
    url = url.format(shop_name)
    r = requests.post(url, headers=headers, json=data)

    if r.status_code != 201:
        logging.error(traceback.format_exc())
        raise ChargeExc('status_code = {}'.format(r.status_code))

    return r.json().get('application_charge').get('confirmation_url')


def get_list_application_charge(shop_name, token, charge_id=None):
    """
    :param shop_name:
    :param token:
    :param charge_id:
    :return: requests json()
    """
    headers = {'X-Shopify-Access-Token': token}
    url = 'https://{}/admin/api/2020-01/application_charges.json'
    params = dict()

    if charge_id:
        params = {'charge_id': charge_id}

    url = url.format(shop_name, charge_id)
    r = requests.get(url, headers=headers, params=params)

    if r.status_code != 200:
        logging.error(traceback.format_exc())
        raise ChargeExc('status_code = {}'.format(r.status_code))

    return r.json()


def get_application_charge(shop_name, token, charge_id):
    """
    :param shop_name:
    :param token:
    :param charge_id:
    :return: requests json()
    """
    headers = {'X-Shopify-Access-Token': token}
    url = 'https://{}/admin/api/2020-01/application_charges/{}.json'
    url = url.format(shop_name, charge_id)
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        logging.error(traceback.format_exc())
        raise ChargeExc('status_code = {}'.format(r.status_code))

    return r.json()


def activate_application_charge(shop_name, token, charge_id, data):
    headers = {'X-Shopify-Access-Token': token}
    url = 'https://{}/admin/api/2020-01/application_charges/{}/activate.json'
    url = url.format(shop_name, charge_id)
    r = requests.post(url, headers=headers, json=data)

    if r.status_code != 200:
        logging.error(traceback.format_exc())
        raise ChargeExc('status_code = {}'.format(r.status_code))

    return r.json()


def run_activate_charge(shop_name, token, charge_id):
    # получаем данные
    data = get_application_charge(shop_name, token, charge_id)

    if data.get('application_charge').get('status') == 'accepted':
        logging.warning('accepted')
        data = activate_application_charge(shop_name, token, charge_id, data)
        logging.warning(data.get('application_charge').get('status'))


def check_status_charge(shop_name, token, charge_id):
    data = get_list_application_charge(shop_name, token, charge_id)
    application_charges = data.get('application_charges')

    if len(application_charges) == 0:
        return False

    if application_charges[0].get('status') == 'active':
        return True

    return False


if __name__ == '__main__':
    shop_name = 'cdek2.myshopify.com'
    token = '6242eefdac6ed587c81241f79792c064'
    charge_id = '12334334087'
    status = check_status_charge(shop_name, token, charge_id)
    print(status)

