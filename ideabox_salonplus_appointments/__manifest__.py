# -*- coding: utf-8 -*-
{
    'name': "Salon Plus Appointment Module",

    'summary': "Module to Customize Appointment Module for Salon Plus",

    'author': "Ideabox Technologies",
    'website': "https://ideabox.technology",

    'category': 'Customization',
    'version': '0.1',

    'depends': ['base','hr','resource','product','appointment', 'point_of_sale','web'],

    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/data.xml',
    ],
    # Muhammad Bilal
    'assets': {
        'point_of_sale._assets_pos': [
            'ideabox_salonplus_appointments/static/src/app/appointment_button/appointment_button.js',
            'ideabox_salonplus_appointments/static/src/app/appointment_button/appointment_button.xml',
            'ideabox_salonplus_appointments/static/src/app/pos_store.js',
            'ideabox_salonplus_appointments/static/src/app/pos_order_line.js',
            'ideabox_salonplus_appointments/static/src/app/order_lines/order_line.js',
            'ideabox_salonplus_appointments/static/src/app/order_lines/order_line.xml',
            
        ],
    },
    'application': True,
    'installable': True,

}

