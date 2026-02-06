# -*- coding: utf-8 -*-

{
    'name': 'Ideabox POS Multi Receipt Print',
    'version': '18.0.0.1',
    'category': 'Point of Sale',
    'summary': '',
    'description': """""",
    'author': 'Muhammad Bilal',
    'website': '',
    "currency": 'EUR',
    'depends': ['base', 'point_of_sale'],
    'data': [],
    'assets': {
        'point_of_sale._assets_pos': [
            'ideabox_pos_multi_receipt/static/src/css/Receipt.css',
            'ideabox_pos_multi_receipt/static/src/css/Screen.css',
            'ideabox_pos_multi_receipt/static/src/app/receipts/receiptscreen.xml',
            'ideabox_pos_multi_receipt/static/src/app/receipts/receiptscreen.js',
            'ideabox_pos_multi_receipt/static/src/app/receipts/models.js',
            'ideabox_pos_multi_receipt/static/src/app/receipts/multi_receipt_screen.xml',
            'ideabox_pos_multi_receipt/static/src/app/receipts/multi_receipt_screen.js',    
            'ideabox_pos_multi_receipt/static/src/app/receipts/multi_pos_receipt.xml',
            'ideabox_pos_multi_receipt/static/src/app/receipts/multi_pos_receipt.js',            
        ],
    },
    'license': 'LGPL-3',
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'live_test_url': '',
    "images": [],
}
