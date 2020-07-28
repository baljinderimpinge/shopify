import os
import pathlib

DEBUG = True
SECRET_KEY = 'Of3JabPx'

DATABASE = {
    'engine': 'peewee.MySQLDatabase',
    'host': '127.0.0.1',
    'name': 'ecocart',
    'user': 'root',
    'passwd': 'root',
    'charset': 'utf8'
}

IP = '127.0.0.1'
PORT = 8001

SHOPIFY_API_VERSION = '2020-01'
SHOPIFY_API_KEY = '980c2450569b83493b4f8b4f1006262f'
SHOPIFY_API_SECRET = '2c92937602ab771a6174c500ecf5fc61'

HOSTNAME = 's.ecocartapp.com'
SCOPE = ['read_orders', 'write_orders',
         'read_products', 'write_products',
         'read_locations',
         'read_script_tags', 'write_script_tags',
         'write_inventory'
         ]

CHARGE_ENABLE = False
CHARGE_NAME = 'All'
CHARGE_TEST = True


WTF_CSRF_ENABLED = False

KEY_CRYPTO = 'VgC08pcJ'
METAFIELD_NAMESPACE = 'ecocart'

# WORK_DIR = pathlib.Path().absolute()
# print('WORK_DIR',WORK_DIR)
# DATA_DIR = os.path.join(WORK_DIR, 'data')
# GEO_DB = 'GeoLite2-City.mmdb'
# PATH_GEO_DB = os.path.join(DATA_DIR, GEO_DB)
# GEO_DB_US = 'us-zip-code-latitude-and-longitude.csv'
# PATH_GEO_DB_US = os.path.join(DATA_DIR, GEO_DB_US)

# заменен на путь к файлу
#ECOCART_SETTINGS_URL = 'https://s.ecocartapp.com/static/ecocart_settings.json'

ECOCART_SETTINGS_PATH = os.path.join('data', 'settings.json')
ECOCART_IMAGE_URL = 'https://s.ecocartapp.com/static/img/ecocart.png'
DEFAULT_SETTINGS_HTML_PATH = os.path.join('static', 'default_settings_html')

DELETE_APP_URL = 'https://admin.ecocart.io/delete-app?merchant_id={}'

try:
    from staging_config import *
except ImportError:
    pass
