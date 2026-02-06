from odoo import api, fields, models, _, Command
from odoo.exceptions import ValidationError,UserError

class AccountMove(models.Model):
    _inherit = "account.move"

    employee_id = fields.Many2one('hr.employee', string='Resource', readonly=True)