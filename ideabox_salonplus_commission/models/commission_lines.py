from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class CommissionLines(models.Model):
    _name = 'commission.lines'
    _description = 'Commission Lines'

    commission_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ], string="Commission Type", required=True)
    
    commission_on = fields.Selection([
        ('onsite', 'Onsite Service'),
        ('offsite', 'Offsite Service'),
        ('referral', 'Referral'),
        ('over_time', 'Over Time'),
    ], string="Commission On", required=True)



    amount = fields.Float(string="Amount", store=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    
    @api.constrains('amount')
    def _check_commission_amount(self):
        for record in self:
            if record.commission_type == 'percentage':
                if record.amount < 0 or record.amount > 100:
                    raise ValidationError("Commission percentage must be between 0 and 100.")
            if record.commission_type == 'fixed':
                if record.amount < 0:
                    raise ValidationError("Fixed commission amount must be non-negative.")

