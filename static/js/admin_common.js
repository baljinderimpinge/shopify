class Admin {
    constructor(idAlert) {
        this.idAlert = idAlert;
    }
    ready() {
        this.f = document.forms[0];
        this.f.addEventListener('submit', (e) => {
            e.preventDefault();
            console.log('form submit');
            this.sendForm();
        })
    }
    async sendForm() {
        let formData = new FormData(this.f);
        let url = location.href;
        try {
            let response = await fetch(url, {
                method: 'POST',
                cache: 'no-cache',
                credentials: 'same-origin',
                body: formData
            });
            this.result = await response.text();
            var s = '';
            if (this.result.length) {
                s = '<div class="alert error"><dl><dt>Error</dt><dd>' + this.result + '</dd></dl></div>';
            } else {
                s = '<div class="alert success"><dl><dt>Success</dt><dd></dd></dl></div>';
            }
            console.log(this);
            document.getElementById(this.idAlert).innerHTML = s;
            setTimeout(() => {
                document.getElementById(this.idAlert).innerHTML = '';
            }, 3000);
        } catch (error) {
            console.log(error);
        }
    }
}


class Company {

    constructor() {
        this.number_of_items_selector = '#number_of_items';
        this.numberOfItems_selector = '#numberOfItems';
        this.ni_values = {
            '0': 99,
            '100': [100, 249],
            '250': [250, 499],
            '500': [500, 999],
            '1000': [1000, 2499],
            '2500': [2500, 4999],
            '5000': [5000, 7499],
            '7500': [7500, 9999],
            '10000': 10000,
        };
        this.yourEstimatedCalc_selector = '#yourEstimatedCalc';
        this.estimateMyCostSelector = '#estimateMyCost';
        this.prefixCalcSelector = '#prefixCalc';
    }

    ready() {
        this.fee = document.forms[0].fee;
        this.estimateMyCost = document.querySelector(this.estimateMyCostSelector);
        this.estimateMyCost.addEventListener('click', (e) => {e.preventDefault(); this.clickEstimateMyCost();});
        this.f = document.forms[0];
        this.numberOfItems = document.querySelector(this.numberOfItems_selector);
        this.ni = document.querySelector(this.number_of_items_selector);
        this.yourEstimatedCalc = document.querySelector(this.yourEstimatedCalc_selector);
        this.prefixCalc = document.querySelector(this.prefixCalcSelector);
        this.prefixCalc.innerHTML = '';


        this.f.weight.addEventListener('input', (e) => {
            e.target.value;
        });
    }

    change_fee() {
        let value = this.fee.value;

        if (value != '3') {
            this.numberOfItems.style.display = 'none';
        }
    }

    load_page() {
        this.change_fee();
    }

    click_fee() {
        this.fee.forEach((e) => {
            e.addEventListener('click', () => {this.change_fee();});
        });
    }

    clickEstimateMyCost() {
        
        this.numberOfItems.style.display = 'block';

    }

    change_number_of_items() {
        this.ni.addEventListener('change', () => {
            var formatter = new Intl.NumberFormat('en-US', {maximumFractionDigits: 0})
            let ni_value = this.ni.value;
            let weight = parseFloat(this.f.weight.value);
            let h = window.ecocart_h;
            let ni_values = this.ni_values[ni_value];
            console.log(ni_values);
            console.log(weight);
            console.log(h);
            var result = '';
            if(Array.isArray(ni_values)) {
                let result_0 = weight * ni_values[0] * h;
                let result_1 = weight * ni_values[1] * h;
                result = '$' + formatter.format(result_0) + '-' + formatter.format(result_1);
                this.prefixCalc.innerHTML = '';
            } else {
                result = weight * ni_values * h;
                result = '$' + formatter.format(result);
                
                console.log('ni_value');
                console.log(ni_values);

                if (ni_values === 99) {
                    this.prefixCalc.innerHTML = 'less than';
                } else if (ni_values === 10000) {
                    this.prefixCalc.innerHTML = 'more than';
                }

            }
            this.yourEstimatedCalc.innerHTML = result;
            console.log(result);
        });
    }

}


function menu() {
    document.querySelectorAll('nav a').forEach((e) => {
        e.href += document.location.search;
    });
}
