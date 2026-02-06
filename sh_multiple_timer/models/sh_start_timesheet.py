# Copyright (C) Softhealer Technologies.

from datetime import datetime

from odoo import _, fields, models
from odoo.exceptions import UserError


class TimesheetEntry(models.Model):
    _name = "sh.start.timesheet"
    _description = "Timesheet Start"

    def _get_employee(self):
        employee = (
            self.env["hr.employee"]
            .sudo()
            .search([("user_id", "=", self.env.user.id)], limit=1)
        )
        if employee:
            return employee

    project_id = fields.Many2one("project.project", string="Project", required=True)
    task_id = fields.Many2one(
        "project.task",
        string="Task",
        domain="[('project_id','=',project_id)]",
        required=True,
    )
    start_date = fields.Datetime("Start Date", default=datetime.now(), readonly=True)
    employee_id = fields.Many2one("hr.employee", required=True)

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        readonly=True,
        default=lambda self: self.env.company,
    )

    def button_start_task(self):
        if not self.employee_id:
            raise UserError(_("Only Employee can start task !"))
        if not self.task_id:
            raise UserError(_("Please Select Task !"))
        self.task_id.action_task_start(employee_id=self.employee_id.id)

        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }
