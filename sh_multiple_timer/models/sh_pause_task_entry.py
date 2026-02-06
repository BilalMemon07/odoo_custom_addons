# Copyright (C) Softhealer Technologies.


from odoo import fields, models

# whenever need to update any task entry value need to update following fields
# duration - microseconds
# difference_time_float - in float time
# difference_time - total time in char formate(00:00:00)


class PauseTaskEntry(models.Model):
    _name = "sh.pause.task.entry"
    _description = "Pause Task Timer Data"

    name = fields.Char("Name")
    user_id = fields.Many2one("res.users", "User Id")
    employee_id = fields.Many2one("hr.employee", "Employee Id")
    start_date = fields.Datetime("Start Time", readonly=True)
    task_id = fields.Many2one("project.task", "Task Id")
    sh_pause_time = fields.Datetime("Pause Time", readonly=True)
    is_task_running = fields.Boolean("Task Running")
    duration = fields.Float("Real Duration")
    # duration = fields.Float('Real Duration', compute='_compute_duration')
    account_analytic_id = fields.Many2one("account.analytic.line", "Timesheet Id")
    difference_time = fields.Char("Actual Time")
    difference_time_float = fields.Float("Rounded Time")

    # =============================
    # for edit timesheet from tree
    # =============================
    def action_edit_timesheet(self):
        for rec in self:
            return {
                "name": "Edit Timesheet",
                "type": "ir.actions.act_window",
                "view_type": "form",
                "view_mode": "form",
                "views": [[False, "form"]],
                "res_model": "sh.edit.timesheet",
                "target": "new",
                "context": {
                    "default_sh_pause_timesheet_id": rec.id,
                    "default_difference_time_float": rec.difference_time_float,
                    "active_id": rec.id,
                },
            }
