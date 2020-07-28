"use strict";


function getPosition(options) {
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
        this.ecocart_product_title = "Carbon Offset for Shipping";
        this.ecocart_product = false;

        //this.beforeSelector = '.btn.btn--secondary.cart__update';
        this.beforeSelector = false;
        this.fixedSelector = false;
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
            if (item.product_title === this.ecocart_product_title) {
                this.ecocart_product = item;
            }
        });

    }

    async getEcocart() {

        if (this.total_price == 0) {
            return;
        }
        if (this.ecocart_product) {
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
            this.beavior = this.ecocartResult.beavior;
            this.variant_id = this.ecocartResult.variant_id;
        } catch (error) {
            console.log(error);
        }
    }

    injectEcocart() {

        console.log('inject ecocart ...');
        console.log(this.ecocart_product);
        try {

            if (this.beforeSelector) {
                this.div = document.createElement('div');
                let before_element = document.querySelector(this.beforeSelector);
                before_element.parentNode.insertBefore(this.div, before_element);

            } else {
                this.div = document.querySelector(this.fixedSelector);
            }

            if (this.ecocart_product) {
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
        if (this.ecocart_product) {
            console.log('ecocart_product exists, return');
            return;
        }
        let re = /##PRICE##/gi;
        this.div.innerHTML = this.json_data.estimate.replace(re, this.calc);
    }

    injectCss(cssUrl) {
        if (document.getElementById(this.cssId)) return;
        let head = document.getElementsByTagName("head")[0];
        let link = document.createElement("link");
        link.id = this.cssId;
        link.rel = "stylesheet";
        link.type = "text/css";
        link.href = cssUrl;
        link.media = "all";
        head.appendChild(link);
    }

    addEventCheckbox() {
        this.checkbox = document.querySelector(this.ecocartCheckbox);
        if (this.checkbox) {
            this.checkbox.addEventListener('change', () => { this.clickCheckbox() });
        }
    }

    async getPosition() {
        try {
            if (this.total_price == 0) return;
            let result = await getPosition();
            this.latitude = result.coords.latitude;
            this.longitude = result.coords.longitude;
        } catch (error) {
            console.log(error);
        }
    }

    async clickCheckbox() {
        if (this.checkbox.checked) {
            console.log(this.variant_id);
            let data = {
                quantity: 1,
                id: this.variant_id,
                requires_shipping: false
            }
            try {
                let response = await fetch("/cart/add.js", {
                    method: 'POST',
                    cache: 'no-cache',
                    credentials: 'same-origin',
                    headers: { 'Content-Type': 'application/json' },
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
        btns[0].onclick = function () {
            par[0].classList.add("checked")
            har[0].classList.add("visible");
        }
    }
    if (bar.length) {
        bar[0].onclick = function () {
            par[0].classList.add("background")
            par[0].classList.add("background");
        }
    }
}

