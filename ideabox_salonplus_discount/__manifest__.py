# -*- coding: utf-8 -*-
{
    "name": "Ideabox SalonPlus Discount",         
    "author": "Muhammad Bilal",     
    "website": "",     
    "support": "",     
    "category": "Point of Sale",   
    "version": "0.0.1",       
    "summary": """""",          
    "description": """""",
    "depends": ["point_of_sale",'hr'],
    "data": [
        'views/pos_config.xml',
        'views/hr_employee_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [ 
            'ideabox_salonplus_discount/static/src/**/*',
        ]
    },
    "images": [],
    "application": True,
    "auto_install": False,
    "license": "OPL-1",
    "installable": True,
}
