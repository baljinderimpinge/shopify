"use strict";


async function ecocartReady() {
    console.log("ecocart ready");
    let jsonUrl = 'https://ecocart.trademinister.net/ecocart.json?shop_name='
    let ecocartUrl = "https://ecocart.trademinister.net/ecocart";
    let cssUrl = "https://ecocart.trademinister.net/static/css/ecocart.css";
    var ecocart = new Ecocart(ecocartUrl, jsonUrl);
    ecocart.injectCss(cssUrl);
    await ecocart.getData();
    await ecocart.getCart();
    ecocart.parseCart();
    ecocart.injectEcocart();
    await ecocart.getPosition();
    await ecocart.getEcocart();
    ecocart.estimate();
    ecocart.addEventCheckbox();
    window.ecocart = ecocart;
    ecocartTmpl();
}


document.addEventListener("DOMContentLoaded", ecocartReady);
