# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd. (<http://devintellecs.com>).
#
##############################################################################
{
    "name": "Auto fill Done Quantity from Reserve Qty",
    "version": '18.0.1.0',
    "category": 'Warehouse',
    "summary": """
                  Odoo app auto fill done Quantities into delivery order | Reserve Quantity | done Qty | delivery order reserved, done Quantities, reserve Quantities, reserve Quantity, done Quantity fill Quantity, Quantity fill up, delivery order
        """,
    "description": """
        Odoo app auto fill done Quantity into delivery order

odoo done Quantities
odoo reserve Quantities
odoo done Quantity
odoo reserve Quantity
odoo done fill Quantity
done Quantity fill up
odoo delivery order

Odoo app auto fill done Quantities into delivery order | Reserve Quantity | done Qty | delivery order reserved, done Quantities, reserve Quantities, reserve Quantity, done Quantity fill Quantity, Quantity fill up, delivery order
    """,
    "sequence": 1,
    "depends": ['sale_stock','stock'],
    "data": [
        'views/stock_move.xml',
    ],
	'demo': [],
	'test': [],
	'css': [],
	'qweb': [],
	'js': [],
	'images': [
		'images/main_screenshot.png'],
	'installable': True,
	'application': True,
	'auto_install': False,
	#========= Author and Support Details =========#
	'author': 'DevIntelle Consulting Service Pvt.Ltd',
	'website': 'https://arne.odoo.com',
	'maintainer': 'DevIntelle Consulting Service Pvt.Ltd',
	'support': 'devintelle@gmail.com',
	'price': 12.0,
	'currency': 'EUR',
}
