{
    'name': 'Partner Ledger No Payment Filter',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Add filter to show partners with no payments in specified date range',
    'description': '''
        This module extends the Partner Ledger report to add a custom filter
        that shows only partners who have no payments within a specified date range.
        
        Usage:
        - Go to Accounting > Reporting > Partner Ledger
        - Enable "Show Partners with No Payments" filter
        - Set the date range
        - Partners without payments in that range will be displayed
    ''',
    'depends': ['account_reports','web'],
    'data': [],
    'assets': {
         'web.assets_backend': [
            'custom_partner_ledger/static/src/xml/*',
            'custom_partner_ledger/static/src/js/partner_ledger_no_payment_filter.js',
        ],
        
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
