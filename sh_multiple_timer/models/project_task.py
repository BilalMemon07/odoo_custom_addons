# Copyright (C) Softhealer Technologies.

from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProjectTask(models.Model):
    _inherit = "project.task"

    task_running = fields.Boolean("Task Running")
    task_runner = fields.Char(string="Task Runner")
    task_runner_ids = fields.Many2many("res.users", string="Task Runners")
    start_time = fields.Datetime("Start Time", copy=False)
    end_time = fields.Datetime("End Time", copy=False)
    total_time = fields.Char("Total Time", copy=False)
    duration = fields.Float("Real Duration", compute="_compute_duration")

    kanban_timer = fields.Char("Kanban Timer")

    is_user_working = fields.Boolean(
        "Is User working ?", compute="_compute_is_user_working"
    )
    end_task_bool = fields.Boolean("End Task", compute="_compute_end_task_bool")

    def _compute_end_task_bool(self):
        for rec in self:
            rec.end_task_bool = rec.timesheet_ids.filtered(lambda r: not r.end_date)

    @api.model
    def get_duration(self, task):
        if task:
            task = self.sudo().browse(int(task))
            if task and task.timesheet_ids.filtered(lambda r: not r.end_date):
                diff = fields.Datetime.from_string(
                    fields.Datetime.now()
                ) - fields.Datetime.from_string(
                    min(
                        task.timesheet_ids.filtered(lambda r: not r.end_date).mapped(
                            "start_date"
                        )
                    )
                )
                if diff:
                    float(diff.days) * 24 + (float(diff.seconds) / 3600)
                    return diff.total_seconds() * 1000

    def _compute_is_user_working(self):
        for rec in self:
            rec.is_user_working = False
            if rec and rec.timesheet_ids:
                timesheet_line = rec.timesheet_ids.filtered(
                    lambda x: x.task_id.id == rec.id and not x.end_date and x.start_date
                )
                if timesheet_line:
                    rec.is_user_working = True
                else:
                    rec.is_user_working = False

    @api.depends("timesheet_ids.unit_amount")
    def _compute_duration(self):
        for rec in self:
            rec.duration = 0.0
            if rec and rec.timesheet_ids:
                timesheet_line = rec.timesheet_ids.filtered(
                    lambda x: x.task_id.id == rec.id and not x.end_date and x.start_date
                )
                if timesheet_line:
                    rec.duration = timesheet_line[0].unit_amount

    # for open start task wizard from form view and kanban view
    # =========================================================
    def action_task_start_custom(self):
        ctx = {
            "active_id": self.id,
            "default_project_id": self.project_id.id,
            "default_task_id": self.id,
        }
        return {
            "type": "ir.actions.act_window",
            "res_model": "sh.start.timesheet",
            "view_mode": "form",
            "target": "new",
            "context": ctx,
            "views": [[False, "form"]],
        }

    def action_task_start(self, employee_id=False):
        vals = {"name": "/", "date": datetime.now()}

        usr_id = self.env.user.id
        employee = False
        if employee_id:
            vals.update({"employee_id": employee_id})
            employee = self.env["hr.employee"].sudo().browse(employee_id)
        else:
            if usr_id:
                emp_search = (
                    self.env["hr.employee"]
                    .sudo()
                    .search([("user_id", "=", usr_id)], limit=1)
                )

                if emp_search:
                    vals.update({"employee_id": emp_search.id})
                    employee = emp_search
        if not employee:
            raise UserError(_("No employee found"))
        # if self.task_running and not self.env.company.sh_allow_multi_user:
        employee = employee.sudo()
        if employee.task_id:
            raise UserError(
                _(
                    "You can not start 2 tasks at same time!\n"
                    "Another timer is running at %s, %s"
                )
                % (employee.task_id.name, employee.task_id.project_id.name)
            )

        # search_pause_entry = self.env["sh.pause.task.entry"].search(
        #     [("task_id", "=", self.id), ("user_id", "=", self.env.user.id)]
        # )
        #
        # if search_pause_entry:
        #     raise UserError(
        #     )

        self.sudo().start_time = datetime.now()
        # add entry in line

        if self:
            vals.update({"start_date": datetime.now()})
            vals.update({"task_id": self.id})

            if self.project_id:
                vals.update({"project_id": self.project_id.id})
                # act_id = self.env["project.project"].sudo().browse(self.project_id.id)
                #
                # if act_id:
                #     vals.update({"account_id": act_id.id})

        account_analytic_id = self.env["account.analytic.line"].sudo().create(vals)

        # customization code
        if account_analytic_id:
            employee.sudo().write({"account_analytic_id": account_analytic_id.id})

        employee.sudo().write({"task_id": self.id, "start_time": datetime.now()})

        self.sudo().write(
            {
                "task_running": True,
                "task_runner": employee.name,
                "task_runner_ids": [(4, self.env.user.id)],
            }
        )
        self.sudo()._cr.commit()

        # user wise customization
        pause_entry_vals = {
            "start_date": datetime.now(),
            "user_id": self.env.user.id,
            "employee_id": employee.id,
            "task_id": self.id,
            # 'name': self.name,
            "name": f"{self.project_id.name} : {self.name}",
            "account_analytic_id": account_analytic_id.id,
            "is_task_running": True,
        }

        pause_id = self.env["sh.pause.task.entry"].sudo().create(pause_entry_vals)
        if pause_id:
            employee.sudo().write({"active_running_task_id": pause_id.id})

        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

    # @api.model
    # def action_user_task_end(self):
    #     usr_id = self.env.user
    #     if usr_id and usr_id.task_id:
    #         usr_id.task_id.action_task_end()
    #     return {}

    def action_task_end(self):
        return {
            "name": "End Task",
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "sh.task.time.account.line",
            "target": "new",
        }

    @api.depends_context("uid")
    @api.depends(
        "display_timesheet_timer", "timer_start", "timer_pause", "total_hours_spent"
    )
    def _compute_display_timer_buttons(self):
        for task in self:
            task.update(
                {
                    "display_timer_start_primary": False,
                    "display_timer_start_secondary": False,
                    "display_timer_stop": False,
                    "display_timer_pause": False,
                    "display_timer_resume": False,
                }
            )

    # def paush_running_timer(self, vals):
    #
    #     usr_id = self.env.user
    #     push_entry_vals = {}
    #
    #     if not usr_id.active_running_task_id:
    #         if usr_id:
    #             push_entry_vals = {
    #                 "user_id": usr_id.id,
    #                 "task_id": self.id,
    #                 # 'name':self.name,
    #                 "name": f"{self.project_id.name} : {self.name}",
    #             }
    #         if usr_id.account_analytic_id:
    #             push_entry_vals.update(
    #                 {
    #                     "account_analytic_id": usr_id.account_analytic_id.id,
    #                 }
    #             )
    #
    #         if vals.get("start_date"):
    #             diff = fields.Datetime.from_string(
    #                 datetime.now()
    #             ) - fields.Datetime.from_string(vals.get("start_date"))
    #             if diff:
    #                 duration = diff.total_seconds() * 1000
    #
    #             push_entry_vals.update(
    #                 {
    #                     "start_date": vals.get("start_date"),
    #                     "sh_pause_time": datetime.now(),
    #                     "duration": duration,
    #                     "difference_time": str(diff).split(".")[0] if diff else False,
    #                     "difference_time_float": diff.total_seconds() / 3600,
    #                 }
    #             )
    #
    #         ative_task_entry = self.env["sh.pause.task.entry"].create(push_entry_vals)
    #
    #         usr_id.write({"active_running_task_id": ative_task_entry.id})
    #
    #     else:
    #         # for add duration if already have old duration
    #         if usr_id.start_time:
    #             diff = fields.Datetime.from_string(
    #                 datetime.now()
    #             ) - fields.Datetime.from_string(usr_id.start_time)
    #
    #             if diff:
    #                 duration = diff.total_seconds() * 1000
    #                 usr_id.sudo().active_running_task_id.duration = (
    #                     usr_id.sudo().active_running_task_id.duration + duration
    #                 )
    #
    #                 if usr_id.sudo().active_running_task_id.difference_time:
    #                     old_difference_time = (
    #                         usr_id.sudo().active_running_task_id.difference_time
    #                     )
    #                     if old_difference_time:
    #
    #                         # IF PAUSE TIMER IS IN DAYS(GREATER THAN 24 HOURS)
    #                         if (
    #                             "day" in old_difference_time
    #                             or "days" in old_difference_time
    #                         ):
    #                             days, old_difference_time = old_difference_time.split(
    #                                 ","
    #                             )
    #                             old_difference_time = old_difference_time.strip()
    #
    #                         conveted_type = datetime.strptime(
    #                             old_difference_time, "%H:%M:%S"
    #                         )
    #                         total_time_task = conveted_type + diff
    #                         if total_time_task:
    #                             usr_id.sudo().active_running_task_id.difference_time = (
    #                                 str(total_time_task.time()).split(".")[0]
    #                             )
    #                 else:
    #                     usr_id.sudo().active_running_task_id.difference_time = str(
    #                         diff
    #                     ).split(".")[0]
    #
    #                 if usr_id.sudo().active_running_task_id.difference_time_float:
    #                     old_difference_time = (
    #                         usr_id.sudo().active_running_task_id.difference_time_float
    #                     )
    #                     usr_id.sudo().active_running_task_id.difference_time_float = (
    #                              diff.total_seconds() / 3600
    #                                         ) + old_difference_time
    #
    #                 else:
    #                     usr_id.sudo().active_running_task_id.difference_time_float = (
    #                         diff.total_seconds() / 3600
    #                     )
    #
    #         usr_id.sudo().active_running_task_id.write(
    #             {"sh_pause_time": datetime.now(), "is_task_running": False}
    #         )
    #
    #     # ======= remove user data from task
    #     self.sudo().write(
    #         {
    #             "start_time": None,
    #             "task_running": False,
    #             "task_runner": False,
    #             "task_runner_ids": [(3, self.env.user.id)],
    #         }
    #     )
    #
    #     # self.env.user.write(
    #     #     {
    #     #         "task_id": False,
    #     #         "account_analytic_id": False,
    #     #         "start_time": False,
    #     #         "active_running_task_id": False,
    #     #     }
    #     # )
    #
    #     self.sudo()._cr.commit()
    #
    #     return {
    #         "type": "ir.actions.client",
    #         "tag": "reload",
    #     }
