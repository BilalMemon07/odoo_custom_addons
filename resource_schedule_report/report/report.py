from datetime import timedelta,datetime
from odoo.exceptions import UserError, AccessError
from odoo import _, api, fields, models


class ResourceScheduleReport(models.AbstractModel):
    _name = "report.resource_schedule_report.resource_schedule_reports"
    _description = "Resource Schedule Report"

    def _get_report_values(self, docids, data=None):
        result = []
        for emp in data.get("employee_ids"):
            employee = self.env['hr.employee'].browse(emp)
            shifts = self.env['resource.calendar.attendance'].search([('employee_id', '=', employee.id)])
            def float_to_12h(time_float):
                """Convert float hour (e.g., 13.5) to 12-hour time string (e.g., '01:30 PM')."""
                hours = int(time_float)
                minutes = int(round((time_float - hours) * 60))
                suffix = "AM"
                if hours >= 12:
                    suffix = "PM"
                display_hour = hours % 12 or 12  # convert 0 -> 12 for 12-hour format
                return f"{display_hour:02}:{minutes:02} {suffix}"
            if shifts:
                for shift in shifts:
                    
                    result.append({
                        'day': shift.name,
                        'employee_name': shift.employee_id.name,
                        'from': float_to_12h(shift.hour_from),
                        'to': float_to_12h(shift.hour_to),
                        'period': dict(shift._fields['day_period'].selection).get(shift.day_period),
                    })
        return {
            "data": result,
        }
