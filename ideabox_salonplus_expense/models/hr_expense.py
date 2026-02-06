from odoo import api, fields, models, _, Command
from odoo.exceptions import ValidationError,UserError


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    def create(self, vals):
        res = super(HrExpenseSheet, self).create(vals)
        res.action_submit_sheet()
        res.action_approve_expense_sheets()
        # res.action_sheet_move_post()
        return res
