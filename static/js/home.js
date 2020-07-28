async function ready() {
    console.log("trm ready");
    let idAlert = 'alertBlock';
    let admin = new Admin(idAlert);
    admin.ready()

    var company = new Company();
    company.ready();
    company.load_page();
    company.click_fee();
    company.change_number_of_items();
    window.company = company;
    menu();
}
 
document.addEventListener("DOMContentLoaded", ready);

ShopifyApp.ready(function() {
    document.querySelector('registration').addEventListener('click', function (e){
        e.preventDefault();
        let a = e.target;
        ShopifyApp.remoteRedirect(a.href);
    });
});