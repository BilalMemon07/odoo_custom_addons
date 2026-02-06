# Part of Odoo. See LICENSE file for full copyright and licensing details.

import math

from odoo import api, fields, models, _
from datetime import datetime, timedelta


class ResourceCalendarAttendance(models.Model):
    _inherit = "resource.calendar.attendance"

    # Add these fields to your model
    date_start = fields.Datetime(compute='_compute_dates', store=False, string='Start DateTime')
    date_stop = fields.Datetime(compute='_compute_dates', store=False, string='End DateTime')
    employee_id = fields.Many2one('hr.employee', string='Employee')

    @api.depends('dayofweek', 'hour_from', 'hour_to')
    def _compute_dates(self):
        today = fields.Date.today()
        # Monday of current week
        monday = today - timedelta(days=today.weekday())

        for attendance in self:
            if attendance.dayofweek and attendance.hour_from and attendance.hour_to:
                specific_day = monday + timedelta(days=int(attendance.dayofweek))
                attendance.date_start = datetime.combine(
                    specific_day, datetime.min.time()
                ) + timedelta(hours=attendance.hour_from - 5)
                attendance.date_stop = datetime.combine(
                    specific_day, datetime.min.time()
                ) + timedelta(hours=attendance.hour_to - 5)
            else:
                attendance.date_start = False
                attendance.date_stop = False