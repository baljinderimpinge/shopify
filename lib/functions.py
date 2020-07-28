import traceback
import json
import csv
import time
import shopify
from geopy.distance import geodesic
import geoip2.database
from lib.shopify_sdk import Sdk
from models import Ecocart_Product, Merchant


def pause_sdk(sleep):
    if shopify.Limits.credit_used() > shopify.Limits.credit_limit() / 2:
        time.sleep(sleep)


def calc_amount(shipping_weight, location_po, shipping_po):
    """
    :param shipping_weight: float lb/фунты
    :param location_po: tuple
    :param shipping_po: tuple
    :return: float
    """
    _offset_shipping_const = 0.000000857244
    _offset_manufacturing_cost = 0.00499
    # mi
    shipping_distance = geodesic(location_po, shipping_po).miles
    offset_shipping = shipping_weight * shipping_distance * _offset_shipping_const
    offset_manufacturing = (33.1354386 + 29.6944507) * 0.00499
    result = offset_shipping + offset_manufacturing + 0.1
    return result


def get_geoloc(ip_address, path_db):
    with geoip2.database.Reader(path_db) as reader:
        response = reader.city(ip_address)
        result = (response.location.latitude, response.location.longitude)
    return result


def get_geoloc_us(zip, city, state, path_db):
    with open(path_db, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader)
        for row in reader:
            if row[0] == zip:
                return (float(row[3]), float(row[4]))
    with open(path_db, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader)
        for row in reader:
            if row[1] == city and row[2] == state:
                return (float(row[3]), float(row[4]))
    return None


class EcocartExc(Exception):
    pass


def get_ecocart_variant(merchant, total_weight, calc_amount):
    ecocart_product = Ecocart_Product.get(Ecocart_Product.merchant == merchant)
    last_variant = ecocart_product.last_variant
    if not last_variant:
        last_variant = 1
    else:
        last_variant += 1
        if last_variant >= 100:
            last_variant = 1
    store = type('Store', (object,), dict(shop_name=merchant.shop_name,
                                          token=merchant.token))
    product = Sdk(store).Product.single(ecocart_product.shopify_product_id)
    #print(json.dumps(product, ensure_ascii=False))
    variants = product.get('product').get('variants')
    count_variants = len(variants)
    u = None  # update product?

    for i in range(1, 100):
        _title = 'Offset up to {} lbs of carbon emissions ({})'.format(total_weight, str(i))
        #_title = 'Offset up to {} lb of carbon emissions'.format(
        #    total_weight)

        if count_variants == i:
            variants.append({
                'product_id': ecocart_product.shopify_product_id,
                'title': _title,
                'price': str(calc_amount),
                'option1': _title,
                'inventory_management': None
            })
            u = True

            break

        variant = variants[i]

        if last_variant == i and variant.get('title') == _title:
            variant.update({
                'price': str(calc_amount),
                'inventory_management': None
            })
            u = True

            break

        if float(variant.get('price')) == calc_amount and variant.get('title') == _title:
            u = False

            break

    if u is None:
        variants.append({
            'product_id': ecocart_product.shopify_product_id,
            'title': _title,
            'price': str(calc_amount),
            'option1': _title,
            'inventory_management': None
        })
        u = True

    if u is False:

        return variant.get('id')

    product = Sdk(store).Product.update(product)
    variant = product.get('product').get('variants')[i]
    variant_id = variant.get('id')

    if variant.get('requires_shipping'):
        inventory_item_data = {
            'inventory_item': {
                'id': variant.get('inventory_item_id'),
                'requires_shipping': False
            }
        }
        _ = Sdk(store).InventoryItem.update(inventory_item_data)

    ecocart_product.last_variant = i
    ecocart_product.save()
    return variant_id


def get_location_address(shop_name, token):
    # из шопа примари локейшин, и его с списка локейшинов выбираю



    store = type('Store', (object,), dict(shop_name=shop_name, token=token))
    locations = Sdk(store).Location.find()
    result = None
    for location in locations.get('locations'):
        if location.get('active'):
            result = {
                'zip': location.get('zip'),
                'city': location.get('city'),
                'state': location.get('province')
            }
            break
    return result

# слежение/создание продукта в базе и магазине
class Ecocart:

    def __init__(self, image_url, merchant=None, shop_name=None, version='2020-01'):
        self.version = version
        self.merchant = merchant
        if not self.merchant:
            self.merchant = Merchant.get(Merchant.shop_name == shop_name)
        self.image_url = image_url

    def check_db(self):
        """
        :param shop_name:
        :return: str or False: shopify product.id
        """
        try:
            self.ecocart_product = Ecocart_Product.get(
                Ecocart_Product.merchant == self.merchant)
            return self.ecocart_product.shopify_product_id
        except Exception:
            self.ecocart_product = False
            traceback.print_exc()
            return False

    def check_store(self, product_id):
        try:
            with shopify.Session.temp(self.merchant.shop_name, self.version,
                                      self.merchant.token):
                product = shopify.Product.find(product_id)
                return product.id
        except:
            return False

    def create_product(self, title='Carbon Neutral Order'):
        store = type('Store', (object,), dict(shop_name=self.merchant.shop_name,
                                              token=self.merchant.token))
        data = {
            'product': {
                'title': title,
                'images': [
                    {
                        'src': self.image_url
                    }
                ]
            }
        }
        response = Sdk(store).Product.create(data)
        product = response.get('product')

        default_variant = product.get('variants')[0]

        if default_variant.get('requires_shipping'):
            inventory_item_data = {
                'inventory_item': {
                    'id': default_variant.get('inventory_item_id'),
                    'requires_shipping': False
                }
            }
            _ = Sdk(store).InventoryItem.update(inventory_item_data)

        product_id = product.get('id')

        if not self.ecocart_product:
            self.ecocart_product = Ecocart_Product()
            self.ecocart_product.merchant = self.merchant

        self.ecocart_product.shopify_product_id = str(product_id)
        self.ecocart_product.save()

        return product_id

    def install(self, title='Carbon Neutral Order'):
        product_id = self.check_db()
        if not product_id:
            product_id = self.create_product(title)
            return product_id
        else:
            product_id = self.check_store(product_id)
            if not product_id:
                product_id = self.create_product(title)
                return product_id
        return product_id


# расчет цены доставки
class EcocartCalc:

    def __init__(self, product_types, primary_product_types, offset_manufacturing_cost,
                 offset_shipping_const, secondary_product_types):

        self.products_type_emissions = product_types
        '''
        self.products_type_emissions = {
            'jeans': 33.1354386,
            'pants': 33.1354386,
            'shorts': 29.6944507,
            'shoes': 13.889106,
            'shirt': 14.881185,
            'skirt': 14.881185,
            'dress, aaaaaa': 22.4147849,
            'jacket': 17.857422,
            'underwear': 1.8847501
        }
        '''
        self.offset_manufacturing_cost = offset_manufacturing_cost
        self.offset_shipping_const = offset_shipping_const
        self.fee = 0.15
        self.primary_product_types = primary_product_types
        self.secondary_product_types = secondary_product_types
        self.run_result = []

    def get_product_type_emissions(self, product_type, product_title):
        #if not product_type:
        #    return self.products_type_emissions.get(self.primary_product_types)

        print('*' * 20)
        print(product_type)
        print(product_title)

        print('-' * 20)
        print(self.secondary_product_types)
        print(self.secondary_product_types)

        for k in self.secondary_product_types:
            print(k)


            if k.lower() in product_type:
                return self.secondary_product_types.get(k)

            if k.lower() in product_title:
                return self.secondary_product_types.get(k)

        return self.products_type_emissions.get(self.primary_product_types)

    def run(self, cart, shipping_distance, default_weight):
        """
        :param cart: json
        :param shipping_distance: mi
        :param default_weight: lb
        :return:
        """

        print('run')

        total_amount = 0
        for item in cart.get('items'):
            grams = item.get('grams', 0)

            if grams:
                weight = grams * 0.002205

            else:
                weight = default_weight

            shipping_weight = weight * item.get('quantity')  # общий вес по позиции
            product_type = item.get('product_type').lower()
            product_title = item.get('product_title').lower()
            product_type_emissions = self.get_product_type_emissions(product_type, product_title)
            print('product_type_emissions')
            print(product_type_emissions)

            offset_shipping = shipping_weight * shipping_distance * self.offset_shipping_const
            offset_manufacturing = product_type_emissions * self.offset_manufacturing_cost
            amount = offset_shipping + offset_manufacturing + self.fee
            total_amount += amount

            self.run_result.append(dict(
                shipping_weight=shipping_weight,
                product_type=product_type,
                product_title=product_title,
                product_type_emissions=product_type_emissions,
                offset_shipping=offset_shipping,
                offset_manufacturing=offset_manufacturing,
                amount=amount,
                shipping_distance=shipping_distance,
                fee=self.fee,
                offset_manufacturing_cost=self.offset_manufacturing_cost,
                offset_shipping_const=self.offset_shipping_const
            ))

        total_amount = round(total_amount, 2)

        return total_amount


def calc_ecocart(cart, shopify_location_address, shipping_po, ip_address,
                 path_db, path_db_us, default_weight, product_types=None,
                 offset_shipping_const=None, offset_manufacturing_cost=None,
                 fee=None, primary_product_types=None, default_shipping_distance=None,
                 secondary_product_types=None):
    zip = shopify_location_address.get('zip')
    city = shopify_location_address.get('city')
    state = shopify_location_address.get('state')
    try:
        location_po = get_geoloc_us(zip, city, state, path_db_us)

        if not location_po:
            raise EcocartExc('location_po is None')
        # вставить поиск для GB

        if not shipping_po:
            shipping_po = get_geoloc(ip_address, path_db)
        shipping_distance = geodesic(location_po, shipping_po).miles
    except:
        print('exc shipping distance')
        shipping_distance = default_shipping_distance

    ecocart_calc = EcocartCalc(product_types, primary_product_types, offset_manufacturing_cost, offset_shipping_const, secondary_product_types)
    amount = ecocart_calc.run(cart, shipping_distance, default_weight)
    return amount, ecocart_calc


def clear_cart(cart, product_id):
    _items = []
    u = False
    for item in cart.get('items'):
        if str(item.get('product_id')) == str(product_id):
            continue
        _items.append(item)
        u = True
    cart.update({
        'items': _items
    })
    return cart, u



