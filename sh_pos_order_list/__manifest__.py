# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
{
    "name": "Point Of Sale Order List",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "point of sale",
    "license": "OPL-1",
    "summary": "POS Restaurant Sync Restaurant order POS Order List POS All Order List on POS screen POS Frontend Orders Management POS Order management POS Order List Management Manage point of sale order Current Session pos order reprint odoo Manage POS Orders Manage POS Orders from the POS Screen POS All Orderlist POS orderlist POS list Point of Sale Orders Display POS Orders Display POS Orders list Display Point of Sale Orders POS Orders Display Point of Sale Orders Display POS Reorder Load All Past Orders in POS POS Past Orders POS Load Previous Orders Track Old Orders in POS Track Orders Manage Point of Sale Orders Point of Sale Order List Session Order list All Order List Load Orders POS Customer Order List Point Of Sale Customer Order List POS History POS Order History POS Customer Order History Point Of Sale History Point Of Sale Order History Point Of Sale Customer Order History",
    "description": """Currently, in odoo there is well designed and precisely managed POS system available. But one thing that everyone wanted in pos is the current session order list on POS Main Screen. The main reason behind this feature is you can easy to see previous orders, easy to do re-order, re-print orders without closing the current session.""",
    "version": "0.0.3",
    "depends": ["point_of_sale"],
    "application": True,
    "data": [
        'views/res_pos_settings.xml',
    ],
    'assets': {'point_of_sale._assets_pos': [
            'sh_pos_order_list/static/src/apps/buttons/order_list_button/*',
            'sh_pos_order_list/static/src/apps/screen/order_list_screen/*',
            'sh_pos_order_list/static/src/scss/pos.scss',
        ]
    },
    "images": ["static/description/background.png", ],
    "auto_install": False,
    "price": 25,
    "installable": True,
}
