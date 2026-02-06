# Copyright (C) Softhealer Technologies.

from datetime import timedelta

from odoo import fields, models


class TimesheetEdit(models.Model):
    _name = "sh.edit.timesheet"
    _description = "Timesheet Edit"

    name = fields.Char("Name")
    sh_pause_timesheet_id = fields.Many2one("sh.pause.task.entry", "Pause Timeshee Id")
    difference_time_float = fields.Float("Rounded Time", required=True)

    def edit_pause_task_timesheet(self):

        if self.sh_pause_timesheet_id and self.difference_time_float:
            updated_time_float = self.difference_time_float
            total_seconds = int(updated_time_float * 3600)
            total_time_in_datetime_formate = timedelta(seconds=total_seconds)

            updated_vals = {
                "difference_time_float": self.difference_time_float,
                "duration": total_seconds * 1000,  # multiple with 1000 for miliseconds
                "difference_time": str(total_time_in_datetime_formate),
            }
            self.sh_pause_timesheet_id.sudo().write(updated_vals)
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }
