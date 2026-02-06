import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    task_id = fields.Many2one("project.task")

    active_running_task_id = fields.Many2one(
        "sh.pause.task.entry", "Active Running Task Info"
    )
    task_running_ids = fields.One2many(
        "sh.pause.task.entry", "employee_id", string="Total Running Tasks"
    )
    start_time = fields.Datetime("Start Time", copy=False)
    end_time = fields.Datetime("End Time", copy=False)
    account_analytic_id = fields.Many2one(
        comodel_name="account.analytic.line", string="Timesheet Id"
    )


class HrEmployee(models.Model):
    _inherit = "hr.employee"


    def _check_private_fields(self, field_names):
        _logger.info("in superp")
        # if not self.env.su:
        #     return super(HrEmployee, self)._check_private_fields(field_names)
        return True
