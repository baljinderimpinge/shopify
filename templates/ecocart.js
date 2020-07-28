"use strict";


function getPosition (options) {
    return new Promise(function (resolve, reject) {
        navigator.geolocation.getCurrentPosition(resolve, reject, options);
    });
}


class Ecocart {

    constructor(ecocartUrl, json_url) {
        console.log("ecocart");
        this.shop_name = window.Shopify.shop;
        this.ecocartUrl = ecocartUrl;
        this.cssId = "ecocartCss";
        this.latitude = null;
        this.longitude = null;
        this.ecocart_product_title = "Carbon Neutral Order";
        this.ecocart_product = false;

        //this.beforeSelector = '.btn.btn--secondary.cart__update';
        this.beforeSelector = false;
        this.afterSelector = false;
        this.fixedSelector = false;
        this.prependSelector = false;
        this.appendSelector = false;

        this.json_url = json_url + this.shop_name;

        this.json_data = false;
        this.ecocartCheckbox = '#ecocart-green-shipping-button';
    }

    async getData() {
        // 1
        console.log('ready...');
        try {
            let response = await fetch(this.json_url);
            this.json_data = await response.json();


        } catch (error) {
            console.error(error);
        }
    }

    async getCart() {
        // 2
        try {
            let response = await fetch("/cart.js");
            this.cart = await response.json();
        } catch (errot) {
            console.error(error);
        }
    }

    parseCart() {
        // 3
        this.total_price = this.cart.total_price;
        this.cart.items.forEach((item) => {
            if(item.product_title === this.ecocart_product_title) {
                this.ecocart_product = item;
            }
        });

    }

    async getEcocart() {

        if(this.total_price == 0) {
            return;
        }
        if(this.ecocart_product) {
            console.log('skip getEcocart');
            return;
        }
        console.log('load ecocart...')
        try {
            let f = new FormData();
            f.append('shop_name', this.shop_name);
            if (this.latitude && this.longitude) {
                f.append('latitude', this.latitude);
                f.append('longitude', this.longitude);
            }
            f.append('cart', JSON.stringify(this.cart));
            let response = await fetch(this.ecocartUrl, {
                method: 'POST',
                mode: 'cors',
                cache: 'no-cache',
                body: f
            });
            this.ecocartResult = await response.json();
            this.calc = this.ecocartResult.calc;
            this.fee = this.ecocartResult.fee;
            this.variant_id = this.ecocartResult.variant_id;
        } catch (error) {
            console.log(error);
        }
    }

    injectEcocart() {
        // встроить экокарт блок и данные
        console.log('inject ecocart ...');
        console.log(this.ecocart_product);
        try {

            /*
            if (!this.beforeSelector && !this.afterSelector && !this.prependSelector && !this.appendSelector && !this.fixedSelector) {
                console.log(Shopify.theme.name);
            }
            */

            if (this.beforeSelector) {
                this.div = document.createElement('div');
                let before_element = document.querySelector(this.beforeSelector);
                before_element.parentNode.insertBefore(this.div, before_element);

            } else if (this.afterSelector) {
                this.div = document.createElement('div');
                let after_element = document.querySelector(this.afterSelector);
                after_element.parentNode.insertBefore(this.div, after_element.nextSibling);

            } else if (this.prependSelector) {
                this.div = document.createElement('div');
                let prepend_element = document.querySelector(this.prependSelector);
                prepend_element.prepend(this.div);

            } else if (this.appendSelector) {
                this.div = document.createElement('div');
                let append_element = document.querySelector(this.appendSelector);
                append_element.append(this.div);

            } else if (this.fixedSelector){
                // fixed
                this.div = document.querySelector(this.fixedSelector);

            } else {
                this.div = document.createElement('div');

                  if (Shopify.theme.name == 'Debut') {
                    let selector = '.cart__shipping';
                    let element = document.querySelector(selector);
                    element.parentNode.insertBefore(this.div, element.nextSibling);

                } else if (Shopify.theme.name == 'Supply') {
                    let selector = '.cart__policies';
                    let element = document.querySelector(selector);
                    element.parentNode.insertBefore(this.div, element.nextSibling);

                } else if (Shopify.theme.name == 'Brooklyn') {
                    let selector = '.cart__row.cart__row--last';
                    let element = document.querySelector(selector);
                    element.parentNode.insertBefore(this.div, element);

                } else if (Shopify.theme.name == 'Narrative') {
                    let selector = '.grid';
                    let element = document.querySelector(selector);
                    element.parentNode.append(this.div);

                } else if (Shopify.theme.name == 'Boundless') {
                    let selector = '.cart__subtotal-container';
                    let element = document.querySelector(selector);
                    element.parentNode.insertBefore(this.div, element);

                } else if (Shopify.theme.name == 'Simple') {
                    let selector = '.cart__footer';
                    let element = document.querySelector(selector);
                    element.parentNode.insertBefore(this.div, element);

                } else if (Shopify.theme.name == 'Minimal') {
                    let selector = '.cart__row--table-large';
                    let element = document.querySelector(selector);
                    element.parentNode.insertAfter(this.div, element);

                } else if (Shopify.theme.name == 'Venture') {
                    let selector = '.responsive-table';
                    let element = document.querySelector(selector);
                    element.parentNode.insertAfter(this.div, element);

                }

                //.cart__policies

            }

            if (this.fee == '3') {
                this.div.innerHTML = this.json_data.shipment;
                return;
            }


            if(this.ecocart_product) {
                console.log('ecocart_product exists');
                this.div.innerHTML = this.json_data.shipment;

            } else {
                this.div.innerHTML = this.json_data.loading;
            }


        } catch (error) {
            console.error(error);
        }
    }

    estimate() {

        if (this.fee == '3') {
            this.div.innerHTML = this.json_data.company;
            return;
        }

        if(this.ecocart_product) {
            console.log('ecocart_product exists, return');
            return;
        }
        let re = /##PRICE##/gi;
        this.div.innerHTML = this.json_data.estimate.replace(re, this.calc);

        // debug
        this.div.innerHTML = this.div.innerHTML + '<!--<div style="word-wrap: break-word;">' + JSON.stringify(this.ecocartResult.run_result) + '<br>for each row<br> offset_shipping = shipping_weight * shipping_distance * self.offset_shipping_const<br>offset_manufacturing = product_type_emissions * self.offset_manufacturing_cost<br>amount = offset_shipping + offset_manufacturing + self.fee </div>-->';

    }

    injectCss(cssUrl) {
        if (document.getElementById(this.cssId)) return;
        cssUrl = cssUrl + this.shop_name;
        let head  = document.getElementsByTagName("head")[0];
        let link  = document.createElement("link");
        link.id   = this.cssId;
        link.rel  = "stylesheet";
        link.type = "text/css";
        link.href = cssUrl;
        link.media = "all";
        head.appendChild(link);
    }

    injectFonts() {
        let url = 'https://fonts.googleapis.com/css?family=Montserrat:100,100i,200,200i,300,300i,400,400i,500,500i,600,600i,700,700i,800,800i,900,900i&display=swap';
        let head  = document.getElementsByTagName("head")[0];
        let link  = document.createElement("link");
        link.id   = 'ecocartFont';
        link.rel  = "stylesheet";
        link.type = "text/css";
        link.href = url;
        link.media = "all";
        head.appendChild(link);
    }

    addEventCheckbox() {
        this.checkbox = document.querySelector(this.ecocartCheckbox);
        if (this.checkbox) {
            this.checkbox.addEventListener('change', () => {this.clickCheckbox()});
        }
    }

    async getPosition() {
        try {
            if(this.total_price == 0) return;
            let result = await getPosition();
            this.latitude = result.coords.latitude;
            this.longitude = result.coords.longitude;
        } catch(error) {
            console.log(error);
        }
    }

    async clickCheckbox() {
        if (this.checkbox.checked) {
            console.log(this.variant_id);
            let data = {
                quantity: 1,
                id: this.variant_id
            }
            try {
                let response = await fetch("/cart/add.js", {
                    method: 'POST',
                    cache: 'no-cache',
                    credentials: 'same-origin',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data),
                });
                let result = await response.json();
                this.ecocartVariant = result;
                location.reload();
            } catch (error) {
                console.log(error);
            }
        }
    }

}

function ecocartTmpl() {
    var btns = document.getElementsByClassName("show-btn")
    var par = document.getElementsByClassName('ecocart')
    var har = document.getElementsByClassName('descr')
    var bar = document.getElementsByClassName("ecocart-checker")
    if (btns.length) {
        btns[0].onclick = function() {
            par[0].classList.toggle("checked")
            har[0].classList.toggle("visible");
        }
    }
    if (bar.length) {
        bar[0].onclick = function(){
            par[0].classList.add("background")
            par[0].classList.add("background");
        }
    }
}


async function ecocartReady() {
    //if (document.location.pathname !== '/cart') return;
    console.log("ecocart ready");
    let jsonUrl = 'https://{{ hostname }}/ecocart.json?shop_name='
    let ecocartUrl = "https://{{ hostname }}/ecocart";
    let cssUrl = "https://{{ hostname }}/ecocart.css?shop_name=";
    var ecocart = new Ecocart(ecocartUrl, jsonUrl);

    {% if selector %}

        {% if placement == 'before' %}

            ecocart.beforeSelector = '{{ selector }}';
        
        {% elif placement == 'after' %}

            ecocart.afterSelector = '{{ selector }}';
        
        {% elif placement == 'prepend' %}

            ecocart.prependSelector = '{{ selector }}';
        
        {% elif placement == 'append' %}

            ecocart.appendSelector = '{{ selector }}';
        
        {% else %}

            ecocart.fixedSelector = '{{ selector }}'

        {% endif %}
    
    {% endif %}

    ecocart.injectCss(cssUrl);
    ecocart.injectFonts();
    await ecocart.getData();
    await ecocart.getCart();
    ecocart.parseCart();
    ecocart.injectEcocart();
    //await ecocart.getPosition();
    await ecocart.getEcocart();
    ecocart.estimate();
    ecocart.addEventCheckbox();
    window.ecocart = ecocart;
    ecocartTmpl();

    {{ js|safe }}
}


//document.addEventListener("DOMContentLoaded", ecocartReady);
ecocartReady();
