# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    "name": "Website Minimum Order Quantity",
    "version": "18.0.0.2",
    "category": "eCommerce",
    "summary": "Minimum Order Quantity on Website product Minimum Quantity Website Minimum Quantity shop Minimum order Quantity in shop Minimum of Quantity in shop Minimum product Quantity website Minimum product Quantity cart minimum order Quantity shop minimum order qty",
    "description": """
        This Odoo App helps users to set minimum order quantity of each products. User can define the minimum order quantity that customer can buy. Customer can buy either the minimum order quantity or more than that quantity, If customer try to buy less than the minimum order quantity then there will be a warning stating that they can not buy less than the minimum order quantity in the website and sale order.
    """,
    "author": "BROWSEINFO",
    "price": 10,
    "currency": "EUR",
    "website": "https://arne.odoo.com",
    "depends": ["base", "base_setup", "website_sale", "sale_management"],
    "data": [
        "views/min_qty_product_view.xml",
        "views/templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "bi_minimum_order_quantity/static/src/js/minimum_qty.js",
            "bi_minimum_order_quantity/static/src/js/optional_product_inherit.js",
        ]
    },
    "license": "OPL-1",
    "auto_install": False,
    "installable": True,
    "live_test_url": "https://www.browseinfo.com/demo-request?app=bi_minimum_order_quantity&version=18&edition=Community",
    "images": ["static/description/Banner.gif"],
}
