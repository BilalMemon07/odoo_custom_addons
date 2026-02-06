# Copyright (C) Softhealer Technologies.

from datetime import datetime

from odoo import api, fields, models


class TaskTimeAccountLine(models.Model):
    _name = "sh.task.time.account.line"
    _description = "Task Time Account Line"

    def _get_default_description(self):
        if self.env.company.sh_allow_without_description:
            return "/"

    name = fields.Text("Description", required=True, default=_get_default_description)
    start_date = fields.Datetime("Start Date", readonly=True)
    end_date = fields.Datetime("End Date", readonly=True)
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee")
    duration = fields.Float("Duration (HH:MM)", readonly=True)

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        readonly=True,
        default=lambda self: self.env.company,
    )
    warning = fields.Char("Warning", readonly=True)

    @api.onchange("employee_id")
    def _onchange_employee_id(self):
        context = dict(self.env.context or {})
        active_model = context.get("active_model", False)
        active_id = context.get("active_id", False)
        task = False
        if active_model == "project.task":
            if active_id:
                task_search = self.env["project.task"].search(
                    [("id", "=", active_id)], limit=1
                )

                if task_search:
                    task = task_search[0]
        if not task:
            self.warning = "No task found, please go to the task to end the timesheets."
            return
        if not self.employee_id:
            self.warning = "Please select an employee."
        if self.employee_id:
            if self.employee_id.task_id == task:
                self.start_date = self.employee_id.start_time
                self.end_date = datetime.now()
                self.duration = (self.end_date - self.start_date).seconds / 3600
                self.warning = False
            else:
                self.warning = (
                    "No started timesheets found of this employee on this task."
                )

    def end_task(self):
        IrConfigParameter = self.env["ir.config_parameter"].sudo()

        context = dict(self.env.context or {})
        active_model = context.get("active_model", False)
        active_id = context.get("active_id", False)

        minimum_duration = int(
            IrConfigParameter.get_param("timesheet_grid.timesheet_min_duration", 0)
        )
        rounding = int(
            IrConfigParameter.get_param("timesheet_grid.timesheet_rounding", 0)
        )
        minutes_spent = self.duration * 60
        time_spent = (
            self.env["timer.mixin"]._timer_rounding(
                minutes_spent, minimum_duration, rounding
            )
            / 60
        )

        vals = {
            "name": self.name,
            "unit_amount": time_spent,
            "amount": time_spent,
            "date": datetime.now(),
        }

        if active_model == "project.task":
            if active_id:
                task_search = self.env["project.task"].search(
                    [("id", "=", active_id)], limit=1
                )

                if task_search:
                    vals.update({"end_date": datetime.now()})
                    vals.update({"task_id": task_search.id})

                    if task_search.project_id:
                        vals.update({"project_id": task_search.project_id.id})
                        act_id = (
                            self.env["project.project"]
                            .sudo()
                            .browse(task_search.project_id.id)
                            .account_id
                        )

                        if act_id:
                            vals.update({"account_id": act_id.id})
                    oldest_ts = task_search.timesheet_ids.filtered(
                        lambda r: not r.end_date and r.employee_id != self.employee_id
                    ).sorted(lambda r: r.start_date, reverse=True)
                    task_search.sudo().write(
                        {
                            "start_time": oldest_ts[0].start_date
                            if oldest_ts
                            else None,
                            "task_running": bool(oldest_ts),
                            "task_runner": oldest_ts[0].employee_id.name
                            if oldest_ts
                            else None,
                            "task_runner_ids": [(3, self.env.user.id)],
                        }
                    )

            # customization code
            if self.employee_id.account_analytic_id:
                self.employee_id.account_analytic_id.sudo().write(vals)

            self.sudo()._cr.commit()

            if self.employee_id.active_running_task_id:
                self.employee_id.sudo().active_running_task_id.write(
                    {"is_task_running": False}
                )
                self.employee_id.sudo().active_running_task_id.unlink()

            self.employee_id.sudo().write(
                {
                    "task_id": False,
                    "account_analytic_id": False,
                    "active_running_task_id": False,
                }
            )

        if active_model == "sh.pause.task.entry":
            if active_id:
                entry_search = self.env["sh.pause.task.entry"].search(
                    [("id", "=", active_id)], limit=1
                )

                if entry_search:
                    vals.update({"end_date": entry_search.sh_pause_time})
                    vals.update({"task_id": entry_search.task_id.id})

                    if entry_search.task_id.project_id:
                        vals.update({"project_id": entry_search.task_id.project_id.id})
                        act_id = (
                            self.env["project.project"]
                            .sudo()
                            .browse(entry_search.task_id.project_id.id)
                            .account_id
                        )
                        if act_id:
                            vals.update({"account_id": act_id.id})

            if entry_search.account_analytic_id:
                entry_search.account_analytic_id.write(vals)
            entry_search.sudo().unlink()

        return {"type": "ir.actions.client", "tag": "reload"}
