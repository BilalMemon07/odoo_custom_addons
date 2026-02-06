from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class TipReport(models.TransientModel):
    _name = 'tip.report'
    _description = 'Tips Report'

    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    employee_ids = fields.Many2many('hr.employee', string='Resource(s)', required=False)
    billing_amount = fields.Boolean(string='Billing Amount', default=True)
    client_name = fields.Boolean(string='Client Name', default=True)
    

    def print_report(self):
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'employee_ids': self.employee_ids.ids if self.employee_ids else [],
            'billing_amount': self.billing_amount,
            'client_name': self.client_name,
        }
        return self.env.ref('ideabox_salonplus_tips.action_report_tip').report_action(self, data=data)