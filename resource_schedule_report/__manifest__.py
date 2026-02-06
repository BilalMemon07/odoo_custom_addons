{
    'name': 'Resource Work Schedule Report',
    'version': '1.2',

    'depends': ['base',  'stock', 'sale','hr'],
    
    'data': [
            'security/ir.model.access.csv',
            'wizard/wizard.xml',
            'report/report.xml',
            'report/report_template.xml',
        
            ],
    
    'author':'Ideabox Technologies',
    
    'installable': True,
    'auto_install': False,
    'application': False,
}
