from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class CommissionReport(models.TransientModel):
    _name = 'commission.report'
    _description = 'Commission Report'

    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    employee_ids = fields.Many2many('hr.employee', string='Resource(s)', required=False)
    

    def print_report(self):
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'employee_ids': self.employee_ids.ids if self.employee_ids else [],
        }
        return self.env.ref('ideabox_salonplus_commission.action_report_commission').report_action(self, data=data)