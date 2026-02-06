{
    'name': 'Ideabox Salon Plus Contact',
    'version': '1.0',
    'summary': '',
    'category': '',
    'author': 'Muhammad Bilal',
    'website': '',
    'depends': ['base', 'contacts','point_of_sale'],
    'data': [
        'data/area_data.xml',
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'views/area_block.xml',
    ],
    'demo': [],
    'assets': {
        'point_of_sale._assets_pos': [
            'ideabox_salonplus_contacts/static/src/app/store/pos_store.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}