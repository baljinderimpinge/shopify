"use strict";


function ecocartTmpl() {
    var btns = document.getElementsByClassName("show-btn")
    var par = document.getElementsByClassName('plashka')
    var har = document.getElementsByClassName('descr')
    var bar = document.getElementsByClassName("ecocart-checker")
    btns[0].onclick = function() {
        par[0].classList.add("checked")
        har[0].classList.add("visible");    
    }
    bar[0].onclick = function(){
        par[0].classList.add("background")
        par[0].classList.add("background");
    }
}


async function ecocartReady() {
    console.log("ecocart ready");
    let ecocartUrl = "https://shopify.ecocartapp.com/ecocart";
    let cssUrl = "https://shopify.ecocartapp.com/static/css/ecocart.css";
    let afterSelector = '.cart__buttons-container';
    let ecocartBlockUrl = "https://shopify.ecocartapp.com/static/html/ecocart.html";
    let ecocart = new Ecocart(ecocartUrl, ecocartBlockUrl);
    let ecocartCheckbox = '#ecocart-green-shipping-button';
    ecocart.injectCss(cssUrl);
    await ecocart.injectEcocart(afterSelector);
    await ecocart.getCart();
    await ecocart.getPosition();
    ecocart.parseCart();
    await ecocart.getEcocart();
    ecocart.populate();
    ecocart.addEventCheckbox(ecocartCheckbox);
    window.ecocart = ecocart;
    ecocartTmpl();
}
 
document.addEventListener("DOMContentLoaded", ecocartReady);
