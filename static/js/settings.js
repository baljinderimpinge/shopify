"use strict";

class Preview {
    constructor() {
        this.id_elements = [
            'estimate',
            'shipment',
            'loading'
        ];
    }

    display(e) {
        let field = e.target;
        let widget_id = field.id + '_preview';
        document.getElementById(widget_id).innerHTML = field.value;
    }

    ready() {
        this.id_elements.forEach((id_element) => {
            let field = document.getElementById(id_element);
            field.addEventListener('input', this.display);
            let widget_id = field.id + '_preview';
            document.getElementById(widget_id).innerHTML = field.value;

        });
    }
}



class CustomizeBlock {
    constructor() {
        this.id_customize = 'customizeBlock';
        this.id_default_view = 'default_view';
    }

    display() {
        if (this.checkbox.value == 'yes') {
            this.block.style.display = 'none';
        } else {
            this.block.style.display = 'block';
            
        }
    }

    ready() {
        this.checkbox = document.forms[0][this.id_default_view];
        this.block = document.getElementById(this.id_customize);
        this.display();
        this.checkbox.forEach((e) => {
            e.addEventListener('change', () => {
                this.display();
            });
        });
            
    }

}


function injectCss(shop_name, cssUrl) {
    let cssId = 'cssIdsettings';
    if (document.getElementById(cssId)) return;
    cssUrl = cssUrl + shop_name;
    let head  = document.getElementsByTagName("head")[0];
    let link  = document.createElement("link");
    link.id   = cssId;
    link.rel  = "stylesheet";
    link.type = "text/css";
    link.href = cssUrl;
    link.media = "all";
    head.appendChild(link);
}


async function resetClick(shop_name) {
    try {
        let response = await fetch("/reset?shop_name=" + shop_name, {
            method: 'GET',
            cache: 'no-cache',
            credentials: 'same-origin',
        });
        let result = await response.text();
        console.log(result);
        location.reload();
    } catch (error) {
        console.log(error);
    }

}



function ready() {
    console.log("trm ready");
    menu();
    let preview = new Preview();
    preview.ready();
    let customize_block = new CustomizeBlock()
    customize_block.ready();
    let idAlert = 'alertBlock';
    let admin = new Admin(idAlert);
    admin.ready()
}



 
document.addEventListener("DOMContentLoaded", ready);