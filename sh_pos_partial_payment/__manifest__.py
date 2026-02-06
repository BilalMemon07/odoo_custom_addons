# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
{
    "name": "Point Of Sale Partial Payment",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "point of sale",
    "license": "OPL-1",
    "summary": "Partial Payment Point Of Sale Partial Payment POS Partial Payment Invoice Partial Payment Invoice Reconciliation Payment Half Payment POS Partially Payment Odoo Partial Invoice Payment Half Payment Point Of Sale Half Payment POS Half Payment Invoice Half Payment Half Invoice Payment Credit Payment Point Of Sale Credit Payment POS Credit Payment Invoice Credit Payment Credit Invoice Reconciliation Payment Credit Payment POS Credit Payment Odoo Credit Invoice Payment POS Partial Credit Payment Point of Sale Partial Credit Payment Split Payment Pay Due Amount POS Due Amount Point of Sale Due Amount Allow to Pay Orders Allow Partial Payment Customer Credit Payment Customer Partial Payment Customer Half Payment Pos Pay Later  POS Partial payments Point of Sale Partial payments POS Part Payment Point of Sale Part Payment Odoo",
    "description": """Using this module customers can pay a partial payment of order. You can restricts the partially payment for all customers and you can allow partial payment feature for special customers as well. We provide filter option to filter partial payment from all the payments.""",
    "version": "0.0.5",
    "depends": ["sh_pos_order_list"],
    "application": True,
    "data": [
        'data/product_product_data.xml',
        'views/account_move_views.xml',
        'views/pos_order_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            # 'sh_pos_partial_payment/static/src/overrides/**/*',
            "sh_pos_partial_payment/static/src/overrides/screens/payment_screen/payment_screen.js",
            "sh_pos_partial_payment/static/src/overrides/models/models.js",
            "sh_pos_partial_payment/static/src/overrides/screens/order_list_screen/order_list_screen.js",
            "sh_pos_partial_payment/static/src/overrides/screens/order_list_screen/order_list_screen.xml",
            "sh_pos_partial_payment/static/src/overrides/screens/order_list_screen/order_list_screen.scss",
        ]
    },
    "images": ["static/description/background.png", ],
    "auto_install": False,
    "installable": True,
    "price": 23.18,
    "currency": "EUR"

}
