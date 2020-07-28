import time
import urllib.parse
import requests


class SdkExc(Exception):
    pass


class Base:
    SLEEP = 2

    def __init__(self, shop_name, token, api_version='2020-04'):
        self.token = token
        self.headers = {'X-Shopify-Access-Token': token}
        self.url = 'https://{shop_name}/admin/api/{api_version}'\
            .format(shop_name=shop_name, api_version=api_version)

    def pause(self, headers):

        try:
            used, limit = headers['X-Shopify-Shop-Api-Call-Limit'].split('/')

            if int(used) >= int(limit) / 20:
                time.sleep(self.SLEEP)

        except:
            pass

    def request(self, method, url, data):
        r = requests.request(method, url, json=data, headers=self.headers)
        self.pause(r.headers)
        return r


class Entity(Base):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create_url = None
        self.update_url = None
        self.delete_url = None
        self.find_url = None
        self.r = None
        self.single_url = None

    def create(self, data):
        r = self.request('POST', self.create_url, data)

        if r.status_code != 201:

            raise SdkExc('!= 201, status_code = {}'.format(r.status_code))

        return r.json()

    def update(self, data):
        r = self.request('PUT', self.update_url, data)

        if r.status_code != 200:

            raise SdkExc('!= 200, status_code = {}'.format(r.status_code))

        return r.json()

    def delete(self):
        r = requests.delete(self.delete_url, headers=self.headers)
        self.pause(r.headers)

        if r.status_code != 200:

            raise SdkExc('!= 200, status_code = {}'.format(r.status_code))

    def find(self, **query):

        if query:
            args = urllib.parse.urlencode(query)
            self.find_url = self.find_url + '?' + args

        r = requests.get(self.find_url, headers=self.headers)
        self.pause(r.headers)

        if r.status_code != 200:

            raise SdkExc('!=200, status_code = {}'.format(r.status_code))

        return r.json()

    def single(self):
        r = requests.get(self.single_url, headers=self.headers)

        if r.status_code != 200:

            raise SdkExc('!= 200, status_code = {}'.format(r.status_code))

        return r.json()


class Product(Entity):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create_url = self.url + '/products.json'
        self.find_url = self.create_url

    def update(self, data):
        self.update_url = self.url + '/products/{}.json'.format(
            data['product']['id'])

        return super().update(data)

    def delete(self, item_id):
        self.delete_url = self.url + '/products/' + str(item_id) + '.json'
        super().delete()

    def single(self, item_id):
        self.single_url = self.url + '/products/' + str(item_id) + '.json'

        return super().single()


class Variant(Entity):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update(self, data):
        self.update_url = self.url + '/variants/{}.json'.format(
            data['variant']['id'])

        return super().update(data)

    def single(self, item_id):
        self.single_url = self.url + '/variants/' + str(item_id) + '.json'

        return super().single()


class Location(Base):

    def find(self):
        url = self.url + '/locations.json'
        r = requests.get(url, headers=self.headers)

        if r.status_code != 200:

            raise SdkExc('!=200, status_code = {}'.format(r.status_code))

        return r.json()


class Webhook(Entity):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create_url = self.url + '/webhooks.json'
        self.find_url = self.create_url

    def delete(self, item_id):
        self.delete_url = self.url + '/webhooks/' + str(item_id) + '.json'
        super().delete()


class InventoryItem(Entity):

    def single(self, item_id):
        self.single_url = self.url + '/inventory_items/{}.json'.format(item_id)

        return super().single()

    def update(self, data):
        self.update_url = self.url + '/inventory_items/{}.json'.format(
            data['inventory_item']['id'])

        return super().update(data)


class Sdk:

    def __init__(self, store):
        self.store = store

    def __getattr__(self, entity):

        if entity == 'Product':

            return Product(self.store.shop_name, self.store.token)

        if entity == 'Variant':

            return Variant(self.store.shop_name, self.store.token)

        if entity == 'Location':

            return Location(self.store.shop_name, self.store.token)

        if entity == 'Webhook':

            return Webhook(self.store.shop_name, self.store.token)

        if entity == 'InventoryItem':

            return InventoryItem(self.store.shop_name, self.store.token)

        raise SdkExc('not exists entity class')
