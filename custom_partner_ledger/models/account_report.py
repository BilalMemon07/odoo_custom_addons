from odoo import models, api, fields, _
from odoo.tools import date_utils
from odoo.tools import SQL
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

class AccountReport(models.Model):
    _inherit = 'account.report'

    def _init_options_payment_date(self, options, previous_options=None):
        """ Initialize payment_date options following the same pattern as date options.
        
        :param dict options: Current report options
        :param dict previous_options: Previous report options
        :return: Updated options
        """
        previous_payment_date = (previous_options or {}).get('payment_date', {})
        # print("payment Date ===>>" +  str(options['payment_date']))
        # Initialize with default values
        options['payment_date'] = {
            'date_from': None,
            'date_to': None,
            'filter': 'custom',
            'mode': 'range',
            'string': _("Payment Date"),
        }
        
        # Copy values from previous options if they exist
        if previous_payment_date:
            options['payment_date'].update({
                'date_from': previous_payment_date.get('date_from'),
                'date_to': previous_payment_date.get('date_to'),
                'filter': previous_payment_date.get('filter', 'custom'),
            })
        
        # Set default dates if not provided (last 30 days)
        # if not options['payment_date']['date_from'] or not options['payment_date']['date_to']:
        #     today = fields.Date.context_today(self)
        #     options['payment_date'].update({
        #         'date_from': (today - relativedelta(days=30)).strftime('%Y-%m-%d'),
        #         'date_to': today.strftime('%Y-%m-%d'),
        #     })
        
        return options
    
    def _get_options_initializers_forced_sequence_map(self):
        """ Add payment_date initializer to the sequence map """
        sequence_map = super()._get_options_initializers_forced_sequence_map()
        sequence_map[self._init_options_payment_date] = 25  # Between date (30) and fiscal_position (20)
        return sequence_map