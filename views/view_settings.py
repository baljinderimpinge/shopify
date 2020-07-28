import json
import traceback
from flask_cors import CORS, cross_origin
from flask import request, render_template, abort
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, RadioField

from lib.signature_validation import signature_validation
from app import app
from models import Merchant, MerchantSettings


class SettingsForm(FlaskForm):
    selector = StringField()
    placement = SelectField(choices=[('before', 'before'), ('after', 'after'),
                                     ('prepend', 'prepend'), ('append', 'append'),
                                     ('fixed', 'replace content')])
    selector_method = SelectField(choices=[('querySelector', 'querySelector'), ('querySelectorAll', 'querySelectorAll')])
    js = TextAreaField()
    default_view = RadioField(choices=[('yes', 'Yes'), ('no', 'No')], default='yes')
    style = TextAreaField()
    estimate = TextAreaField()
    shipment = TextAreaField()
    loading = TextAreaField()
    error_field = TextAreaField()


@app.route('/settings', methods=['GET', 'POST'])
@cross_origin()
def settings_view():
    shop_name = request.args.get('shop')

    if not shop_name:
        abort(403)

    try:
        # проверка подписи
        if not signature_validation(request.args.items(),
                                    app.config['SHOPIFY_API_SECRET']):
            raise Exception('bad sign')

        merchant = Merchant.get(Merchant.shop_name == shop_name)

    except:
        app.logger.warning(traceback.format_exc())
        abort(403)

    if request.method == 'POST':
        form = SettingsForm()

        if form.validate():
            print(form.data)

            try:
                settings = MerchantSettings.get(MerchantSettings.merchant == merchant)

            except MerchantSettings.DoesNotExist:
                settings = MerchantSettings()
                settings.merchant = merchant

            settings.selector = form.data.get('selector')
            settings.placement = form.data.get('placement')
            settings.selector_method = form.data.get('selector_method')
            settings.js = form.data.get('js')
            default_view = True if form.data.get('default_view') == 'yes' else False
            settings.default_view = default_view
            settings.style = form.data.get('style')
            settings.estimate = form.data.get('estimate')
            settings.shipment = form.data.get('shipment')
            settings.loading = form.data.get('loading')
            settings.error_field = form.data.get('error_field')
            settings.save()

            return ''

        else:
            errors = form.errors
            _errors = ['{} - {}<br>'.format(k, errors[k]) for k in errors]
            _errors = ''.join(_errors)
            return _errors

    else:
        try:
            settings = MerchantSettings.get(MerchantSettings.merchant == merchant)
            selector = settings.selector if settings.selector else ''
            placement = settings.placement if settings.placement else ''
            selector_method = settings.selector_method if settings.selector_method else ''
            js = settings.js if settings.js else ''
            default_view = 'yes' if settings.default_view else 'no'
            style = settings.style if settings.style else ''
            estimate = settings.estimate if settings.estimate else ''
            shipment = settings.shipment if settings.shipment else ''
            loading = settings.loading if settings.loading else ''
            error_field = settings.error_field if settings.error_field else ''
            form = SettingsForm(
                selector=selector,
                placement=placement,
                selector_method=selector_method,
                js=js,
                default_view=default_view,
                style=style,
                estimate=estimate,
                shipment=shipment,
                loading=loading,
                error_field=error_field
            )

        except MerchantSettings.DoesNotExist:
            form = SettingsForm()


    return render_template('settings.html', form=form, company=settings.company,
                           url_dashboard=settings.url_dashboard,
                           enable=merchant.enable, shop_name=shop_name, hostname=app.config.get('HOSTNAME'))