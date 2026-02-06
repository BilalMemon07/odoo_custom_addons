# Copyright (C) Softhealer Technologies.

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    start_date = fields.Datetime("Start Date", readonly=True)
    end_date = fields.Datetime("End Date", readonly=True)

    # ===============================================
    # for default category if allow default categories
    # ===============================================

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountAnalyticLine, self).create(vals_list)
        for vals in vals_list:

            # FOR NOT CREATEING WITHOUT HOURS SPEND IN TIMEHSEET VIEW
            if "unit_amount" in vals:
                if vals.get("unit_amount") == 0:

                    raise UserError(_("Please enter your hours. Thank you!"))
            # ========================================================

        return res

    def unlink(self):
        if self.employee_id:
            self.employee_id.task_id = False
            self.employee_id.start_time = False
            self.employee_id.end_time = False
            self.employee_id.account_analytic_id = False
        return super(AccountAnalyticLine, self).unlink()

    def _check_can_write(self, values):
        # If it's a basic user then check if the timesheet is his own.
        pass

    def _check_can_create(self):
        # override in other modules to check current user has create access
        pass
