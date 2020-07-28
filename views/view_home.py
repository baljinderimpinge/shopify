import locale
import json
import urllib
import traceback
from flask_cors import CORS, cross_origin
import requests
from flask import request, render_template, abort, redirect
from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, FloatField, RadioField, \
    BooleanField, StringField, validators
import shopify
import pyactiveresource

from lib.signature_validation import signature_validation
from app import app
from models import Merchant
#from forms import SettingsForm


def reinstall_app(shop_name):
    app.logger.info('reinstall app for {}'.format(shop_name))
    args = urllib.parse.urlencode({'shop': shop_name})
    url = 'https://{}/authorize?{}'
    # редирект в админку
    return redirect(url.format(app.config.get('HOSTNAME'), args))


class SettingsForm(FlaskForm):
    production = BooleanField('Production')
    account_manager_name = StringField()
    account_manager_title = StringField()
    number_of_employees = IntegerField()
    fee = RadioField(choices=[
        ('15', 'Customer'),
        ('3', 'Company')
    ], default='15')

    weight = FloatField('Average Item Weight (default)', [validators.NumberRange(min=0.1)])
    weight_unit = SelectField(choices=[('lbs', 'Lbs')])
    product_types = SelectField('STORE CATEGORY')
    number_of_items = SelectField('Number of items sold per month', choices=[
        ('0', 'Less than 100'),
        ('100', '100-250'),
        ('250', '250-500'),
        ('500', '500-1,000'),
        ('1000', '1,000-2,500'),
        ('2500', '2,500-5,000'),
        ('5000', '5,000-7,500'),
        ('7500', '7,500-10,000'),
        ('10000', 'More than 10,000'),
    ])


@app.route('/app', methods=['GET', 'POST'])
@cross_origin()
def home():
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
            email = shop.email
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

    #r = requests.get(app.config.get('ECOCART_SETTINGS_URL'))
    #ecocart_settings = r.json()
    with open(app.config.get('ECOCART_SETTINGS_PATH')) as f:
        ecocart_settings = json.load(f)

    product_types = ecocart_settings.get('product_types').items()
    product_types = sorted(product_types, key=lambda item: item[1], reverse=True)
    #product_types = [(row[0], '{} - {}'.format(row[0], row[1])) for row in
    #                 product_types]
    product_types = [(row[0], row[0]) for row in product_types]

    h = ecocart_settings.get('h', 1)
    estimated_calc = ''

    if request.method == 'POST':
        form = SettingsForm()
        form.product_types.choices = product_types
        if form.validate():
            settings = form.data

            # пересчитаем в граммы
            default_weight = 0

            if settings.get('weight_unit') == 'lbs':
                default_weight = float(settings.get('weight'))

            default_weight = round(default_weight, 2)
            settings.update({'default_weight': default_weight})
            settings = json.dumps(settings)
            merchant.settings = settings
            merchant.save()
            return ''
        else:
            errors = form.errors
            _errors = ['{} - {}<br>'.format(k, errors[k]) for k in errors]
            _errors = ''.join(_errors)
            return _errors

    else:
        settings = merchant.settings

        if settings:
            settings = json.loads(settings)

        else:
            settings = dict()

        form = SettingsForm(**settings)
        form.product_types.choices = product_types
        prefix_calc = ''

        try:
            ni_values = {
                '0': 99,
                '100': [100, 249],
                '250': [250, 499],
                '500': [500, 999],
                '1000': [1000, 2499],
                '2500': [2500, 4999],
                '5000': [5000, 7499],
                '7500': [7500, 9999],
                '10000': 10000,
            }
            default_weight = settings.get('default_weight')
            number_of_items = settings.get('number_of_items')
            print(default_weight)
            print(number_of_items)
            ni = ni_values.get(number_of_items)
            print('ni')
            print(ni)
            locale.setlocale(locale.LC_ALL, 'en_US.utf8')

            if isinstance(ni, list):
                result_0 = int(default_weight * ni[0] * h)
                result_1 = int(default_weight * ni[1] * h)
                result_0 = locale.format_string('%d', result_0, True)
                result_1 = locale.format_string('%d', result_1, True)
                estimated_calc = '${}-{}'.format(result_0, result_1)

            else:
                estimated_calc = default_weight * ni * h
                estimated_calc = locale.format_string('%d', estimated_calc, True)
                estimated_calc = '$' + str(estimated_calc)

                if ni == 99:
                    prefix_calc = 'less than'

                elif ni == 10000:
                    prefix_calc = 'more than'

            print(estimated_calc)


        except:
            pass

    return render_template('home.html', form=form, ecocart_h=h,
                           estimated_calc=estimated_calc, shop_name=shop_name,
                           enable=merchant.enable, email=email,
                           prefix_calc=prefix_calc)


@app.route('/app2', methods=['GET', 'POST'])
@cross_origin()
def home2():
    shop_name = request.args.get('shop')
    merchant = Merchant.get(Merchant.shop_name == shop_name)
    if request.method == 'POST':
        form = SettingsForm()
        if form.validate():
            settings = json.dumps(form.data)
            merchant.settings = settings
            merchant.save()
            return ''
        else:
            errors = form.errors
            _errors = ['{} - {}<br>'.format(k, errors[k]) for k in errors]
            _errors = ''.join(_errors)
            return _errors
    else:
        settings = merchant.settings
        if settings:
            settings = json.loads(settings)
        else:
            settings = dict()
        form = SettingsForm(**settings)
    return render_template('home.html', form=form)