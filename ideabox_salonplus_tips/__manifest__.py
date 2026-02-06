# -*- coding: utf-8 -*-
{
    'name': "Salon Plus Tips Module",

    'summary': "Module to Allow Custom Tips",

    'author': "Ideabox Technologies",
    'website': "https://ideabox.technology",

    'category': 'Customization',
    'version': '0.1',

    'depends': ['base','hr','resource','product','point_of_sale','hr_expense'],
    
    'assets': {
        'point_of_sale._assets_pos': [
            'ideabox_salonplus_tips/static/src/**/*',
        ],

        },    

    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'report/report.xml',
        'report/report_template.xml',
        'wizard/tip_report.xml',
        'data/data.xml',
    ],
    'application': True,
    'installable': True,

}

