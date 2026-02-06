# -*- coding: utf-8 -*-
{
    'name': "Salon Plus Commission Module",

    'summary': "Module to Allow Product Commissions",

    'author': "Ideabox Technologies",
    'website': "https://ideabox.technology",

    'category': 'Customization',
    'version': '0.1',

    'depends': ['base','hr','resource','product','point_of_sale'],
    
    'assets': {
        'point_of_sale._assets_pos': [
            'ideabox_salonplus_commission/static/src/**/*',
        ],

        },  
    
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'wizard/commission_disbursement.xml',
        'wizard/commission_report.xml',
        'report/report_template.xml',
        'report/report.xml',
        'data/data.xml',
    ],
    'application': True,
    'installable': True,

}

